"""Property management API endpoints."""

import csv
import io
from typing import List, Optional
from uuid import UUID

from dependencies import get_current_user, get_organization_id
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import StreamingResponse
from models.property import (
    Property,
    PropertyBulkCreate,
    PropertyBulkResponse,
    PropertyCreate,
    PropertyExport,
    PropertyFilter,
    PropertyGroup,
    PropertyGroupCreate,
    PropertyGroupListResponse,
    PropertyGroupMemberAction,
    PropertyGroupUpdate,
    PropertyImport,
    PropertyImportResponse,
    PropertyListResponse,
    PropertyUpdate,
)
from models.user import User
from services.property_service import PropertyService
from services.supabase import supabase_service
from supabase import Client

router = APIRouter(prefix="/properties", tags=["Properties"])


def get_supabase_client() -> Client:
    """Provide the shared Supabase client instance."""
    return supabase_service.client


# Property CRUD Endpoints


@router.post("/", response_model=Property, status_code=status.HTTP_201_CREATED)
async def create_property(
    property_data: PropertyCreate,
    current_user: User = Depends(get_current_user),
    service: PropertyService = Depends(lambda: PropertyService()),
):
    """Create a new property."""
    # Verify user belongs to organization
    if property_data.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create property for different organization",
        )

    # Check user role
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and managers can create properties",
        )

    return await service.create_property(property_data, current_user.id)


@router.get("/", response_model=PropertyListResponse)
async def list_properties(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    property_type: Optional[str] = None,
    status: Optional[str] = None,
    manager_id: Optional[UUID] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    group_id: Optional[UUID] = None,
    include_archived: bool = False,
    current_user: User = Depends(get_current_user),
    service: PropertyService = Depends(lambda: PropertyService()),
):
    """List properties with optional filters."""
    filters = PropertyFilter(
        search=search,
        property_type=property_type,
        status=status,
        manager_id=manager_id,
        city=city,
        state=state,
        group_id=group_id,
        include_archived=include_archived,
    )

    properties, total = await service.get_properties(
        filters=filters, user_id=current_user.id, page=page, per_page=per_page
    )

    return PropertyListResponse(
        properties=properties,
        total=total,
        page=page,
        per_page=per_page,
        has_next=page * per_page < total,
        has_prev=page > 1,
    )


@router.get("/{property_id}", response_model=Property)
async def get_property(
    property_id: UUID,
    current_user: User = Depends(get_current_user),
    service: PropertyService = Depends(lambda: PropertyService()),
):
    """Get a single property by ID."""
    return await service.get_property(property_id, current_user.id)


@router.put("/{property_id}", response_model=Property)
async def update_property(
    property_id: UUID,
    property_data: PropertyUpdate,
    current_user: User = Depends(get_current_user),
    service: PropertyService = Depends(lambda: PropertyService()),
):
    """Update an existing property."""
    # Get property to check permissions
    property = await service.get_property(property_id, current_user.id)

    # Check permissions
    if current_user.role == "admin":
        # Admins can update any property in their org
        if property.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot update property from different organization",
            )
    elif current_user.role == "manager":
        # Managers can only update assigned properties
        if property.manager_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only update properties assigned to you",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to update property",
        )

    return await service.update_property(property_id, property_data, current_user.id)


@router.delete("/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_property(
    property_id: UUID,
    hard_delete: bool = Query(False),
    current_user: User = Depends(get_current_user),
    service: PropertyService = Depends(lambda: PropertyService()),
):
    """Delete a property (soft delete by default)."""
    # Only admins can delete properties
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete properties",
        )

    # Get property to verify organization
    property = await service.get_property(property_id, current_user.id)
    if property.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete property from different organization",
        )

    await service.delete_property(property_id, current_user.id, hard_delete)


# Bulk Operations


@router.post("/bulk", response_model=PropertyBulkResponse)
async def bulk_create_properties(
    bulk_data: PropertyBulkCreate,
    current_user: User = Depends(get_current_user),
    service: PropertyService = Depends(lambda: PropertyService()),
):
    """Create multiple properties at once."""
    # Check user role
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and managers can create properties",
        )

    # Verify all properties are for user's organization
    for property_data in bulk_data.properties:
        if property_data.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="All properties must belong to your organization",
            )

    result = await service.bulk_create_properties(bulk_data, current_user.id)
    return PropertyBulkResponse(**result)


# Import/Export


@router.post("/import", response_model=PropertyImportResponse)
async def import_properties(
    file: UploadFile = File(...),
    skip_errors: bool = Query(True),
    dry_run: bool = Query(False),
    current_user: User = Depends(get_current_user),
    service: PropertyService = Depends(lambda: PropertyService()),
):
    """Import properties from CSV or Excel file."""
    # Check user role
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and managers can import properties",
        )

    # Validate file type
    if not file.filename.endswith((".csv", ".xlsx")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be CSV or Excel format",
        )

    # Read file content
    content = await file.read()

    # Process CSV for now (Excel support can be added later)
    if file.filename.endswith(".csv"):
        csv_reader = csv.DictReader(io.StringIO(content.decode("utf-8")))

        imported = 0
        skipped = 0
        errors = []
        preview = []

        for row_num, row in enumerate(csv_reader, start=2):
            try:
                # Map CSV columns to property fields
                property_data = PropertyCreate(
                    organization_id=current_user.organization_id,
                    name=row.get("name", row.get("address", f"Property {row_num}")),
                    address=row["address"],
                    city=row["city"],
                    state=row["state"],
                    zip=row["zip"],
                    country=row.get("country", "USA"),
                    property_type=row.get("type", "other"),
                    manager_id=current_user.id,  # Default to current user
                )

                if dry_run:
                    preview.append(property_data)
                else:
                    await service.create_property(property_data, current_user.id)
                    imported += 1

            except KeyError as e:
                error_msg = f"Row {row_num}: Missing required field {str(e)}"
                errors.append({"row": row_num, "error": error_msg})
                if not skip_errors:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg
                    )
                skipped += 1
            except Exception as e:
                error_msg = f"Row {row_num}: {str(e)}"
                errors.append({"row": row_num, "error": error_msg})
                if not skip_errors:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg
                    )
                skipped += 1

        return PropertyImportResponse(
            total_rows=row_num - 1,
            imported=imported,
            skipped=skipped,
            errors=errors,
            preview=preview if dry_run else None,
        )

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Excel import not yet implemented",
    )


@router.get("/export", response_class=StreamingResponse)
async def export_properties(
    format: str = Query("csv", pattern="^(csv|json)$"),
    include_deleted: bool = Query(False),
    current_user: User = Depends(get_current_user),
    service: PropertyService = Depends(lambda: PropertyService()),
):
    """Export properties to CSV or JSON."""
    # Get all properties
    filters = PropertyFilter(include_archived=include_deleted)
    properties, _ = await service.get_properties(
        filters=filters, user_id=current_user.id, page=1, per_page=10000  # Export all
    )

    if format == "csv":
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(
            [
                "name",
                "address",
                "city",
                "state",
                "zip",
                "country",
                "type",
                "status",
                "manager_id",
                "square_footage",
                "year_built",
                "units",
                "amenities",
            ]
        )

        # Write data
        for prop in properties:
            writer.writerow(
                [
                    prop.name,
                    prop.address,
                    prop.city,
                    prop.state,
                    prop.zip,
                    prop.country,
                    prop.property_type,
                    prop.status,
                    str(prop.manager_id) if prop.manager_id else "",
                    prop.details.square_footage if prop.details else "",
                    prop.details.year_built if prop.details else "",
                    prop.details.units if prop.details else "",
                    ",".join(prop.amenities) if prop.amenities else "",
                ]
            )

        output.seek(0)
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode()),
            media_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="properties.csv"'},
        )

    elif format == "json":
        # Return JSON
        import json

        json_data = json.dumps(
            [prop.dict() for prop in properties], default=str, indent=2
        )
        return StreamingResponse(
            io.BytesIO(json_data.encode()),
            media_type="application/json",
            headers={"Content-Disposition": 'attachment; filename="properties.json"'},
        )


# Property Groups


@router.post(
    "/groups", response_model=PropertyGroup, status_code=status.HTTP_201_CREATED
)
async def create_property_group(
    group_data: PropertyGroupCreate,
    current_user: User = Depends(get_current_user),
    service: PropertyService = Depends(lambda: PropertyService()),
):
    """Create a new property group."""
    # Check permissions
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and managers can create groups",
        )

    # Verify organization
    if group_data.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create group for different organization",
        )

    return await service.create_property_group(group_data, current_user.id)


@router.get("/groups", response_model=PropertyGroupListResponse)
async def list_property_groups(
    current_user: User = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client),
):
    """List all property groups in the organization."""
    # Get groups from database
    result = (
        supabase.table("property_groups")
        .select("*")
        .eq("organization_id", str(current_user.organization_id))
        .execute()
    )

    groups = [PropertyGroup(**g) for g in result.data]

    # Get property counts
    for group in groups:
        count_result = (
            supabase.table("property_group_members")
            .select("property_id", count="exact")
            .eq("group_id", str(group.id))
            .execute()
        )
        group.property_count = count_result.count or 0

    return PropertyGroupListResponse(groups=groups, total=len(groups))


@router.post("/groups/{group_id}/members", status_code=status.HTTP_204_NO_CONTENT)
async def add_properties_to_group(
    group_id: UUID,
    member_data: PropertyGroupMemberAction,
    current_user: User = Depends(get_current_user),
    service: PropertyService = Depends(lambda: PropertyService()),
):
    """Add properties to a group."""
    # Check permissions
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and managers can manage group members",
        )

    await service.add_properties_to_group(
        group_id, member_data.property_ids, current_user.id
    )


@router.delete("/groups/{group_id}/members", status_code=status.HTTP_204_NO_CONTENT)
async def remove_properties_from_group(
    group_id: UUID,
    member_data: PropertyGroupMemberAction,
    current_user: User = Depends(get_current_user),
    service: PropertyService = Depends(lambda: PropertyService()),
    supabase: Client = Depends(get_supabase_client),
):
    """Remove properties from a group."""
    # Check permissions
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and managers can manage group members",
        )

    # Remove properties
    for property_id in member_data.property_ids:
        supabase.table("property_group_members").delete().eq(
            "group_id", str(group_id)
        ).eq("property_id", str(property_id)).execute()
