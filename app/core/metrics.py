# app/core/metrics.py
import asyncio

from prometheus_client import Counter, Histogram, Gauge
import time
from functools import wraps
from typing import Callable

# Authentication Metrics
auth_login_attempts = Counter(
    'radegast_auth_login_attempts_total',
    'Total login attempts',
    ['status']  # success, failed
)

auth_registrations = Counter(
    'radegast_auth_registrations_total',
    'Total user registrations',
    ['status']  # success, failed
)

# Course Metrics
course_operations = Counter(
    'radegast_course_operations_total',
    'Total course operations',
    ['operation', 'status']  # operation: create, update, delete, list, get
)

active_courses = Gauge(
    'radegast_active_courses',
    'Number of active courses'
)

# Teacher Assignment Metrics
teacher_assignments = Counter(
    'radegast_teacher_assignments_total',
    'Total teacher assignments',
    ['operation', 'status']  # operation: assign, remove, update
)

teachers_per_course = Histogram(
    'radegast_teachers_per_course',
    'Number of teachers assigned per course',
    buckets=[1, 2, 3, 5, 10, 20]
)

# API Response Time Metrics
api_response_time = Histogram(
    'radegast_api_response_time_seconds',
    'API response time in seconds',
    ['endpoint', 'method', 'status_code'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
)

# Database Operation Metrics
db_query_duration = Histogram(
    'radegast_db_query_duration_seconds',
    'Database query duration',
    ['operation'],  # select, insert, update, delete
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0]
)

# Error Metrics
api_errors = Counter(
    'radegast_api_errors_total',
    'Total API errors',
    ['endpoint', 'error_type', 'status_code']
)

# Active Users Metric
active_users = Gauge(
    'radegast_active_users',
    'Number of active users by role',
    ['role']  # ADMIN, TEACHER, STUDENT
)


# Decorator for tracking endpoint metrics
def track_endpoint_metrics(endpoint_name: str):
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            status_code = 200
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status_code = getattr(e, 'status_code', 500)
                api_errors.labels(
                    endpoint=endpoint_name,
                    error_type=type(e).__name__,
                    status_code=status_code
                ).inc()
                raise
            finally:
                duration = time.time() - start_time
                api_response_time.labels(
                    endpoint=endpoint_name,
                    method='POST',
                    status_code=status_code
                ).observe(duration)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            status_code = 200
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                status_code = getattr(e, 'status_code', 500)
                api_errors.labels(
                    endpoint=endpoint_name,
                    error_type=type(e).__name__,
                    status_code=status_code
                ).inc()
                raise
            finally:
                duration = time.time() - start_time
                api_response_time.labels(
                    endpoint=endpoint_name,
                    method='GET',
                    status_code=status_code
                ).observe(duration)

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator