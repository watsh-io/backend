import jwt
from .exceptions import TokenHandlingError



def create_token(payload: dict, jwt_secret: str, algorithm: str) -> str:
    """
    Create a JWT token with the provided payload, secret and algorithm.
    
    :param payload: The payload to encode in the token.
    :param jwt_secret: The secret key for encoding the token.
    :param algorithm: The algorithm to use for encoding the token.
    :return: A Token object with the access token.
    :raises TokenHandlingError: If there is an error encoding the token.
    """
    try:
        token = jwt.encode(
            payload, jwt_secret, algorithm=algorithm
        )
    except jwt.PyJWTError as error:
        raise TokenHandlingError(str(error))
    else:
        return token

def decode_token(token: str, jwt_secret: str, algorithm: str) -> dict:
    """
    Decode a JWT token to its payload.
    
    :param token: The JWT token to decode.
    :param jwt_secret: The secret key used for decoding the token.
    :param algorithm: The algorithm used for decoding the token.
    :return: A dict object.
    :raises TokenHandlingError: If there is an error decoding the token.
    """
    try:
        payload = jwt.decode(token, jwt_secret, algorithms=[algorithm])
    except jwt.PyJWTError as error:
        raise TokenHandlingError(str(error))
    else:
        return payload
