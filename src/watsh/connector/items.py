from bson import ObjectId
from motor.core import AgnosticClient
from typing import Any
from jsonschema import protocols, validate

from . import access_control, validation
from .crud import items as crud_items, commits as crud_commits
from src.watsh.lib.models import Item, ItemType, ItemUpdate
from src.watsh.lib.time import now_ms
from src.watsh.lib.pyobjectid import NULL_OBJECTID
from src.watsh.lib.exceptions import BadRequest, ItemNotFound, JSONSchemaError
from src.watsh.lib.crypto import encrypt, decrypt



async def create(
    client: AgnosticClient,
    current_user_id: ObjectId,
    project_id: ObjectId,
    environment_id: ObjectId,
    branch_id: ObjectId,
    parent_id: ObjectId,
    item_type: ItemType,
    slug: str, 
    secret_value: Any,
    secret_active: bool,
    commit_message: str,
    aes_password: str,
) -> ObjectId:
    # Arrays
    if item_type ==ItemType.ARRAY:
        raise Exception('Array not yet supported')
    
    # Start a transaction to ensure that all the inserts are performed atomically.
    async with await client.start_session() as session:
        async with session.start_transaction():
            
            # Access control
            await access_control.user_authorization(
                client=client, session=session, project_id=project_id, user_id=current_user_id
            )

            # Verify project is not archived
            await validation.project_validation(
                client=client, session=session, project_id=project_id, check_is_not_archive=True
            )

            # Verify environment ID
            await validation.environment_validation(
                client=client, session=session, project_id=project_id, environment_id=environment_id,
            )

            # Verify branch ID
            await validation.branch_validation(
                client=client, session=session, project_id=project_id, environment_id=environment_id, branch_id=branch_id, 
            )

            # Check parent exists, is active, and is either an object or an array
            if parent_id != NULL_OBJECTID:
                parent_item = await crud_items.get_item(
                    client=client,
                    session=session,
                    project_id=project_id,
                    environment_id=environment_id,
                    branch_id=branch_id,
                    item_id=parent_id
                )
                
                if parent_item.type not in [ItemType.OBJECT.value, ItemType.ARRAY.value]:
                    raise BadRequest('Parent item can only be an object or array.')

#                 if parent_item.type == ItemType.ARRAY:
#                     # TODO: slug must be the next item index (0, 1, 2, ...)
#                     ...

            # Create the commit
            timestamp = now_ms()

            commit_id = await crud_commits.create_commit(
                client=client, session=session, current_user_id=current_user_id, project_id=project_id,
                environment_id=environment_id, branch_id=branch_id, commit_message=commit_message, timestamp=timestamp
            )
            
            # Create the item
            item_id = ObjectId()

            encrypted_secret = encrypt(aes_password, str(secret_value))

            await crud_items.create_item(
                client=client, session=session, project_id=project_id, environment_id=environment_id,
                branch_id=branch_id, parent_id=parent_id, item_id=item_id, item_slug=slug, item_type=item_type,
                item_active=True, secret_value=encrypted_secret, secret_active=secret_active, commit_id=commit_id, timestamp=timestamp,
            )

            # Commit the transaction
            await session.commit_transaction()
    
    return item_id



async def list_items(
    client: AgnosticClient, 
    current_user_id: ObjectId, 
    project_id: ObjectId,
    environment_id: ObjectId,
    branch_id: ObjectId,
    aes_password: str,
) -> list[Item]:
    # Start a transaction to ensure that all the inserts are performed atomically.
    async with await client.start_session() as session:
        async with session.start_transaction():
            
            # Access control
            await access_control.user_authorization(
                client=client, session=session, project_id=project_id, user_id=current_user_id
            )

            # Verify environment ID
            await validation.environment_validation(
                client=client, session=session, project_id=project_id, environment_id=environment_id,
            )

            # Verify branch ID
            await validation.branch_validation(
                client=client, session=session, project_id=project_id, environment_id=environment_id, branch_id=branch_id, 
            )

            # Get items
            items = await crud_items.list_items(
                client=client,
                session=session,
                project_id=project_id,
                environment_id=environment_id,
                branch_id=branch_id
            )

            for item in items:
                decrypted_secret = decrypt(aes_password, item.secret_value)
                item.secret_value = verify_secret(item.type, decrypted_secret)

            # Commit the transaction
            await session.commit_transaction()

    return items



async def list_items_by_parent(
    client: AgnosticClient, 
    current_user_id: ObjectId, 
    project_id: ObjectId,
    environment_id: ObjectId,
    branch_id: ObjectId,
    parent_id: ObjectId,
    aes_password: str,
) -> list[Item]:
    # Start a transaction to ensure that all the inserts are performed atomically.
    async with await client.start_session() as session:
        async with session.start_transaction():
            
            # Access control
            await access_control.user_authorization(
                client=client, session=session, project_id=project_id, user_id=current_user_id
            )

            # Verify environment ID
            await validation.environment_validation(
                client=client, session=session, project_id=project_id, environment_id=environment_id,
            )

            # Verify branch ID
            await validation.branch_validation(
                client=client, session=session, project_id=project_id, environment_id=environment_id, branch_id=branch_id, 
            )

            # Get items
            items = await crud_items.list_items_per_parent(
                client=client,
                session=session,
                project_id=project_id,
                environment_id=environment_id,
                branch_id=branch_id,
                parent_id=parent_id,
            )

            for item in items:
                decrypted_secret = decrypt(aes_password, item.secret_value)
                item.secret_value = verify_secret(item.type, decrypted_secret)

            # Commit the transaction
            await session.commit_transaction()

    return items


async def get(
    client: AgnosticClient, 
    current_user_id: ObjectId, 
    project_id: ObjectId,
    environment_id: ObjectId,
    branch_id: ObjectId,
    item_id: ObjectId,
    aes_password: str,
) -> Item:
    # Start a transaction to ensure that all the inserts are performed atomically.
    async with await client.start_session() as session:
        async with session.start_transaction():
            
            # Access control
            await access_control.user_authorization(
                client=client, session=session, project_id=project_id, user_id=current_user_id
            )

            # Get item
            item = await crud_items.get_item(
                client=client,
                session=session,
                project_id=project_id,
                environment_id=environment_id,
                branch_id=branch_id,
                item_id=item_id
            )

            decrypted_secret = decrypt(aes_password, item.secret_value)
            item.secret_value = verify_secret(item.type, decrypted_secret)
            
            # Commit the transaction
            await session.commit_transaction()

    return item



async def slug_update(
    client: AgnosticClient, 
    current_user_id: ObjectId, 
    project_id: ObjectId,
    environment_id: ObjectId,
    branch_id: ObjectId,
    item_id: ObjectId,
    slug: str, 
    commit_message: str,
) -> ObjectId:    
    # Start a transaction to ensure that all the inserts are performed atomically.
    async with await client.start_session() as session:
        async with session.start_transaction():
            
            # Access control
            await access_control.user_authorization(
                client=client, session=session, project_id=project_id, user_id=current_user_id
            )

            # Verify project is not archived
            await validation.project_validation(
                client=client, session=session, project_id=project_id, check_is_not_archive=True
            )

            # Verify environment ID
            await validation.environment_validation(
                client=client, session=session, project_id=project_id, environment_id=environment_id,
            )

            # Verify branch ID
            await validation.branch_validation(
                client=client, session=session, project_id=project_id, environment_id=environment_id, branch_id=branch_id, 
            )

            # Create the commit
            timestamp = now_ms()

            commit_id = await crud_commits.create_commit(
                client=client, session=session, current_user_id=current_user_id, project_id=project_id,
                environment_id=environment_id, branch_id=branch_id, commit_message=commit_message, timestamp=timestamp
            )
            
            # Get item
            item = await crud_items.get_item(
                client=client,
                session=session,
                project_id=project_id,
                environment_id=environment_id,
                branch_id=branch_id,
                item_id=item_id
            )

            # Create new item version
            item_version_id = await crud_items.create_item(
                client=client, session=session, project_id=project_id, environment_id=environment_id,
                branch_id=branch_id, parent_id=item.parent, item_id=item_id, item_slug=slug, item_type=item.type,
                item_active=True, secret_value=item.secret_value, secret_active=item.secret_active, commit_id=commit_id, timestamp=timestamp,
            )

            # Commit the transaction
            await session.commit_transaction()

    return item_version_id


async def delete(
    client: AgnosticClient, 
    current_user_id: ObjectId, 
    project_id: ObjectId,
    environment_id: ObjectId,
    branch_id: ObjectId,
    item_id: ObjectId,
    commit_message: str,
) -> None:
    # Start a transaction to ensure that all the inserts are performed atomically.
    async with await client.start_session() as session:
        async with session.start_transaction():
            
            # Access control
            await access_control.user_authorization(
                client=client, session=session, project_id=project_id, user_id=current_user_id
            )

            # Verify project is not archived
            await validation.project_validation(
                client=client, session=session, project_id=project_id, check_is_not_archive=True
            )

            # Verify environment ID
            await validation.environment_validation(
                client=client, session=session, project_id=project_id, environment_id=environment_id,
            )

            # Verify branch ID
            await validation.branch_validation(
                client=client, session=session, project_id=project_id, environment_id=environment_id, branch_id=branch_id, 
            )
            
            # Create the commit
            timestamp = now_ms()

            commit_id = await crud_commits.create_commit(
                client=client, session=session, current_user_id=current_user_id, project_id=project_id,
                environment_id=environment_id, branch_id=branch_id, commit_message=commit_message, timestamp=timestamp
            )
            
            # Get item
            item = await crud_items.get_item(
                client=client,
                session=session,
                project_id=project_id,
                environment_id=environment_id,
                branch_id=branch_id,
                item_id=item_id
            )

            # Create new item version
            await crud_items.create_item(
                client=client, session=session, project_id=project_id, environment_id=environment_id,
                branch_id=branch_id, parent_id=item.parent, item_id=item_id, item_slug=item.slug, item_type=item.type,
                item_active=False, secret_value=None, secret_active=False, commit_id=commit_id, timestamp=timestamp,
            )

            # Commit the transaction
            await session.commit_transaction()



async def list_items_per_commit(
    client: AgnosticClient,
    current_user_id: ObjectId,
    project_id: ObjectId,
    environment_id: ObjectId,
    branch_id: ObjectId,
    commit_id: ObjectId,
    aes_password: str,
) -> list[Item]:
    # Start a transaction to ensure that all the inserts are performed atomically.
    async with await client.start_session() as session:
        async with session.start_transaction():
            
            # Access control
            await access_control.user_authorization(
                client=client, session=session, project_id=project_id, user_id=current_user_id
            )

            # Verify environment ID
            await validation.environment_validation(
                client=client, session=session, project_id=project_id, environment_id=environment_id,
            )

            # Verify branch ID
            await validation.branch_validation(
                client=client, session=session, project_id=project_id, environment_id=environment_id, branch_id=branch_id, 
            )

            # Get commit
            commit = await crud_commits.get_commit(
                client=client,
                session=session,
                project_id=project_id,
                environment_id=environment_id,
                branch_id=branch_id,
                commit_id=commit_id,
            )

            # Get items at this commit
            item_versions = await crud_items.list_items_per_commit(
                client=client,
                session=session,
                project_id=project_id,
                environment_id=environment_id,
                branch_id=branch_id,
                commit_timestamp=commit.timestamp,
            )

            for item in item_versions:
                decrypted_secret = decrypt(aes_password, item.secret_value)
                item.secret_value = verify_secret(item.type, decrypted_secret)

            # Commit the transaction
            await session.commit_transaction()
    
    return item_versions


def verify_secret(item_type: ItemType, secret_value: str) -> str | int | float | bool | None:
    try:

        item_type = ItemType(item_type)

        if item_type == ItemType.STRING:
            return str(secret_value)
        
        elif item_type == ItemType.INTEGER:
            return int(secret_value)

        elif item_type == ItemType.NUMBER:
            return float(secret_value)

        elif item_type == ItemType.BOOLEAN:
            if secret_value.lower() not in ['true', '1', 't']:
                raise ValueError()
            return bool(secret_value)

        elif item_type == ItemType.NULL:
            if secret_value.lower() not in ['none', 'null', '0']:
                raise ValueError()
            return None
        
        elif item_type == ItemType.OBJECT:
            return None
        
        else:
            raise Exception('Wrong item type.')

    except ValueError:
        raise BadRequest(f'Wrong secret format: {item_type} vs {secret_value}')


async def create_secret(
    client: AgnosticClient,
    current_user_id: ObjectId,
    project_id: ObjectId,
    environment_id: ObjectId,
    branch_id: ObjectId,
    item_id: ObjectId,
    secret: str,
    commit_message: str,
    aes_password: str,
) -> None:
    # Start a transaction to ensure that all the inserts are performed atomically.
    async with await client.start_session() as session:
        async with session.start_transaction():
            
            # Access control
            await access_control.user_authorization(
                client=client, session=session, project_id=project_id, user_id=current_user_id
            )

            # Verify project is not archived
            await validation.project_validation(
                client=client, session=session, project_id=project_id, check_is_not_archive=True
            )

            # Verify environment ID
            await validation.environment_validation(
                client=client, session=session, project_id=project_id, environment_id=environment_id,
            )

            # Verify branch ID
            await validation.branch_validation(
                client=client, session=session, project_id=project_id, environment_id=environment_id, branch_id=branch_id, 
            )

            # Get corresponding item
            snapshot_item = await crud_items.get_item(
                client=client,
                session=session,
                project_id=project_id,
                environment_id=environment_id,
                branch_id=branch_id,
                item_id=item_id
            )

            if snapshot_item.type in [ItemType.OBJECT, ItemType.ARRAY]:
                raise BadRequest(f'{snapshot_item.type} cannot hold secrets.')
            
            # Check the secret match the item schema
            casted_secret = verify_secret(ItemType[snapshot_item.type], secret)

            # Create the commit
            timestamp = now_ms()

            commit_id = await crud_commits.create_commit(
                client=client, session=session, current_user_id=current_user_id, project_id=project_id,
                environment_id=environment_id, branch_id=branch_id, commit_message=commit_message, timestamp=timestamp
            )

            # Update the item
            encrypted_secret = encrypt(aes_password, str(casted_secret))

            await crud_items.create_item(
                client=client, session=session, project_id=project_id, environment_id=environment_id,
                branch_id=branch_id, parent_id=snapshot_item.parent, item_id=item_id, item_slug=snapshot_item.slug, item_type=snapshot_item.type,
                item_active=True, secret_value=encrypted_secret, secret_active=True, commit_id=commit_id, timestamp=timestamp,
            )

            # Commit the transaction
            await session.commit_transaction()
    

async def delete_secret(
    client: AgnosticClient,
    current_user_id: ObjectId,
    project_id: ObjectId,
    environment_id: ObjectId,
    branch_id: ObjectId,
    item_id: ObjectId,
    commit_message: str,
) -> None:
    # Start a transaction to ensure that all the inserts are performed atomically.
    async with await client.start_session() as session:
        async with session.start_transaction():
            
            # Access control
            await access_control.user_authorization(
                client=client, session=session, project_id=project_id, user_id=current_user_id
            )

            # Verify project is not archived
            await validation.project_validation(
                client=client, session=session, project_id=project_id, check_is_not_archive=True
            )

            # Verify environment ID
            await validation.environment_validation(
                client=client, session=session, project_id=project_id, environment_id=environment_id,
            )

            # Verify branch ID
            await validation.branch_validation(
                client=client, session=session, project_id=project_id, environment_id=environment_id, branch_id=branch_id, 
            )

            # Get corresponding item
            snapshot_item = await crud_items.get_item(
                client=client,
                session=session,
                project_id=project_id,
                environment_id=environment_id,
                branch_id=branch_id,
                item_id=item_id
            )

            # Create the commit
            timestamp = now_ms()

            commit_id = await crud_commits.create_commit(
                client=client, session=session, current_user_id=current_user_id, project_id=project_id,
                environment_id=environment_id, branch_id=branch_id, commit_message=commit_message, timestamp=timestamp
            )

            # Update the item
            await crud_items.create_item(
                client=client, session=session, project_id=project_id, environment_id=environment_id,
                branch_id=branch_id, parent_id=snapshot_item.parent, item_id=item_id, item_slug=snapshot_item.slug, item_type=snapshot_item.type,
                item_active=True, secret_value=None, secret_active=False, commit_id=commit_id, timestamp=timestamp,
            )

            # Commit the transaction
            await session.commit_transaction()
    



async def create_from_schema(
    client: AgnosticClient, current_user_id: ObjectId,
    project_id: ObjectId, environment_id: ObjectId, branch_id: ObjectId,
    json_schema: dict, json_values: dict, commit_message: str, aes_password: str,
) -> None:
    # Validate json schema
    protocols.Validator.check_schema(json_schema)
    validate(json_values, json_schema)

    async with await client.start_session() as session:
        async with session.start_transaction():
            
            # Access control
            await access_control.user_authorization(
                client=client, session=session, project_id=project_id, user_id=current_user_id
            )

            # Verify project is not archived
            await validation.project_validation(
                client=client, session=session, project_id=project_id, check_is_not_archive=True
            )

            # Verify environment ID
            await validation.environment_validation(
                client=client, session=session, project_id=project_id, environment_id=environment_id,
            )

            # Verify branch ID
            await validation.branch_validation(
                client=client, session=session, project_id=project_id, environment_id=environment_id, branch_id=branch_id, 
            )

            # TODO: Update project description and slug

            # Root keys
            try:
                root_item_type = json_schema['type']
                root_item_properties = json_schema['properties']
            except KeyError as exc: 
                raise JSONSchemaError('The JSON schema miss a key: {exc}')
            
            # The JSON schema must start with an `object` type
            try:
                root_item_type_str = str(root_item_type)
            except ValueError: 
                raise JSONSchemaError('The `type` key is not a dict.')
            
            if not root_item_type_str.lower() == ItemType.OBJECT.value:
                raise JSONSchemaError('The JSON schema must start with an `object` type.')

            # The `properties` key must be a dict.
            try:
                root_item_properties_dict = dict(root_item_properties)
            except ValueError: 
                raise JSONSchemaError('The `properties` key is not a dict.')

            # Create the commit
            timestamp = now_ms()

            commit_id = await crud_commits.create_commit(
                client=client, session=session, current_user_id=current_user_id, project_id=project_id,
                environment_id=environment_id, branch_id=branch_id, commit_message=commit_message, timestamp=timestamp
            )

            # For each property
            item_ids = []

            async def update_items(properties: dict, parent_id: ObjectId, parent_type: ItemType, secret_node: dict) -> None:
                for slug, value in properties.items():
                    
                    # Check parent type
                    if not parent_type in [ItemType.OBJECT, ItemType.ARRAY]:
                        raise JSONSchemaError(f'{parent_type} used as a container.')

                    # Retrieve the item type
                    item_type = ItemType[str(value['type']).upper()]
                    
                    # Retrieve or create the item Id                    
                    try:
                        snapshot_item = await crud_items.get_item_by_slug(
                            client=client, session=session, project_id=project_id, environment_id=environment_id,
                            branch_id=branch_id, parent_id=parent_id, slug=slug
                        )
                        item_id = snapshot_item.item
                    except ItemNotFound:
                        item_id = ObjectId()

                    item_ids.append(item_id)

                    # Get secret
                    secret_value = None
                    secret_active = False

                    if not item_type in [ItemType.ARRAY, ItemType.OBJECT]:
                        try:
                            secret_value = verify_secret(item_type, secret_node[slug])
                            secret_active = True
                        except KeyError:
                            raise JSONSchemaError('All item require a secret for now.')

                    # Update the item
                    encrypted_secret = encrypt(aes_password, str(secret_value))

                    await crud_items.create_item(
                        client=client, session=session, project_id=project_id, environment_id=environment_id,
                        branch_id=branch_id, parent_id=parent_id, item_id=item_id, item_slug=slug, item_type=item_type,
                        item_active=True, secret_value=encrypted_secret, secret_active=secret_active, commit_id=commit_id, timestamp=timestamp,
                    )

                    # Go to child node
                    if item_type == ItemType.ARRAY:
                        raise Exception('Not supported yet.')
                    elif item_type == ItemType.OBJECT:
                        await update_items(value['properties'], item_id, item_type, secret_node[slug])
                        
            await update_items(root_item_properties_dict, NULL_OBJECTID, ItemType.OBJECT, json_values)

            # Delete all items not in schema
            items = await crud_items.list_items(
                client=client, session=session, project_id=project_id, environment_id=environment_id, branch_id=branch_id
            )
            
            encrypted_secret = encrypt(aes_password, str(None))

            for item in items:
                if item.item not in item_ids:
                    await crud_items.create_item(
                        client=client, session=session, project_id=project_id, environment_id=environment_id,
                        branch_id=branch_id, parent_id=item.parent, item_id=item.item, item_slug=item.slug, item_type=item.type,
                        item_active=False, secret_value=encrypted_secret, secret_active=False, commit_id=commit_id, timestamp=timestamp,
                    )

            # Commit the transaction
            await session.commit_transaction()
    
    return commit_id


async def create_from_updates(
    client: AgnosticClient, current_user_id: ObjectId,
    project_id: ObjectId, environment_id: ObjectId, branch_id: ObjectId,
    updates: list[ItemUpdate], commit_message: str, aes_password: str,
) -> ObjectId:
    
    # Start a transaction to ensure that all the inserts are performed atomically.
    async with await client.start_session() as session:
        async with session.start_transaction():
            
            # Access control
            await access_control.user_authorization(
                client=client, session=session, project_id=project_id, user_id=current_user_id
            )

            # Verify project is not archived
            await validation.project_validation(
                client=client, session=session, project_id=project_id, check_is_not_archive=True
            )

            # Verify environment ID
            await validation.environment_validation(
                client=client, session=session, project_id=project_id, environment_id=environment_id,
            )

            # Verify branch ID
            await validation.branch_validation(
                client=client, session=session, project_id=project_id, environment_id=environment_id, branch_id=branch_id, 
            )

            # Create the commit
            timestamp = now_ms()

            commit_id = await crud_commits.create_commit(
                client=client, session=session, current_user_id=current_user_id, project_id=project_id,
                environment_id=environment_id, branch_id=branch_id, commit_message=commit_message, timestamp=timestamp
            )

            # Process updates
            async def delete_all_children(item_id: ObjectId) -> None:
                childrens = await crud_items.list_items_per_parent(
                    client=client, session=session, project_id=project_id, environment_id=environment_id,
                    branch_id=branch_id, parent_id=item_id,
                )

                encrypted_secret = encrypt(aes_password, str(None))

                for child in childrens:
                    await crud_items.create_item(
                        client=client, session=session, project_id=project_id, environment_id=environment_id,
                        branch_id=branch_id, parent_id=child.parent, item_id=child.item, item_slug=child.slug, item_type=child.type,
                        item_active=False, secret_value=encrypted_secret, secret_active=False, commit_id=commit_id, timestamp=timestamp,
                    )

                    if ItemType(child.type) in [ItemType.ARRAY, ItemType.OBJECT]:
                        await delete_all_children(child.item)


            async def process_update(update: ItemUpdate) -> None:
                # Cast the secret value with the right corresponding type
                casted_secret = None

                if update.secret_value:
                    # Check that OBJECT and ARRAY have not secret value
                    if update.type in [ItemType.OBJECT, ItemType.ARRAY]:
                        raise BadRequest(f'{update.type} cannot hold secrets.')
                
                    casted_secret = verify_secret(update.type, update.secret_value)

                # Get the item
                try:
                    item = await crud_items.get_item(
                        client=client, session=session, project_id=project_id, environment_id=environment_id,
                        branch_id=branch_id, item_id=update.item,
                    )

                    if item.type != ItemType(update.type).value:
                        raise BadRequest(f'Item type cannot change.')
                    
                    if item.parent != update.parent:
                        raise BadRequest(f'Item parent cannot change.')
                    
                except ItemNotFound:
                    
                    if not update.active:
                        return
                    
                    # check the slug is not already taken
                    try:
                        await crud_items.get_item_by_slug(
                            client=client, session=session, project_id=project_id, environment_id=environment_id,
                            branch_id=branch_id, parent_id=update.parent, slug=update.slug,
                        )
                    except ItemNotFound:
                        pass
                    else:
                        raise BadRequest(f'Slug already taken.')
                
                
                # update or create the item
                encrypted_secret = encrypt(aes_password, str(casted_secret))

                await crud_items.create_item(
                    client=client, session=session, project_id=project_id, environment_id=environment_id,
                    branch_id=branch_id, parent_id=update.parent, item_id=update.item, item_slug=update.slug, item_type=update.type,
                    item_active=update.active, secret_value=encrypted_secret, secret_active=update.secret_active, commit_id=commit_id, timestamp=timestamp,
                )
                
                if not update.active and ItemType(update.type) in [ItemType.OBJECT, ItemType.ARRAY]:
                    # Delete all children items
                    await delete_all_children(update.item)
                    

            def filter_updates(updates: list[ItemUpdate], parent_id: ObjectId) -> list[ItemUpdate]:
                return [update for update in updates if update.parent == parent_id]
            
            async def process_updates(updates: list[ItemUpdate], parent_id: ObjectId) -> None:
                # Get the updates of the parent and process
                filtered_updates = filter_updates(updates, parent_id)

                for update in filtered_updates:
                    await process_update(update)
                    updates.remove(update)

                # Get the list of items in current container
                parents = await crud_items.list_items_per_parent(
                    client=client, session=session, project_id=project_id, environment_id=environment_id,
                    branch_id=branch_id, parent_id=parent_id,
                )

                # Process updates in hierarchical order, starting from parent
                for parent in parents:
                    if ItemType(parent.type) in [ItemType.OBJECT, ItemType.ARRAY]:
                        await process_updates(updates, parent.item)

            # Process updates in hierarchical order, starting from null
            await process_updates(updates, NULL_OBJECTID)
        
            # Commit the transaction
            await session.commit_transaction()
    
    return commit_id