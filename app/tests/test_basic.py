import pytest
from app.core.redis_config import redis
from app.core.logging_config import loggers
import os

def test_redis_connection(redis_client):
    # Test Redis connection
    test_key = 'test_key'
    test_value = {'test': 'value'}
    
    # Set value
    assert redis_client.set(test_key, test_value)
    
    # Get value
    retrieved_value = redis_client.get(test_key)
    assert retrieved_value == test_value
    
    # Delete value
    assert redis_client.delete(test_key)
    assert not redis_client.exists(test_key)

def test_logging(test_logger):
    # Test logging
    root_logger = test_logger['root']
    api_logger = test_logger['api']
    
    # Test root logger
    root_logger.info('Test root logger message')
    
    # Test API logger
    api_logger.info('Test API logger message')
    
    # Verify log files exist
    assert os.path.exists('logs')
    log_files = [f for f in os.listdir('logs') if f.endswith('.log')]
    assert len(log_files) > 0

def test_database_connection(client):
    # Test database connection through API
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json() == {'status': 'healthy'} 