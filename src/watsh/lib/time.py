from datetime import datetime, timezone

def now() -> int:
    """
    Return the current UTC time since the epoch in seconds.
    
    :return: The number of seconds since the epoch as an integer.
    """
    return int(datetime.now(timezone.utc).timestamp())

def now_ms() -> int:
    """
    Return the current UTC time since the epoch in milliseconds.
    
    :return: The number of milliseconds since the epoch as an integer.
    """
    return int(datetime.now(timezone.utc).timestamp() * 1000)