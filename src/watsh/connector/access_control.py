from bson import ObjectId
from motor.core import AgnosticClient, AgnosticClientSession

from .crud import members as crud_members
from src.watsh.lib.exceptions import UnauthorizedException


async def user_authorization(
    client: AgnosticClient, 
    session: AgnosticClientSession, 
    project_id: ObjectId, 
    user_id: ObjectId,
) -> None:
    if not await crud_members.is_user_member_of_project(
        client=client, 
        session=session, 
        project_id=project_id, 
        user_id=user_id
    ):
        raise UnauthorizedException('You do not have access to this project.')
