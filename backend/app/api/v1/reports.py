"""Reports API endpoints for generating and managing reports."""

from datetime import datetime, date as date_type
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import settings
from app.core.security import get_current_user_db
from app.models.user import User
from app.models.farm import Farm
from app.models.report import Report, ReportStatus
from app.schemas.report import ReportRequest, ReportResponse, ReportListResponse
from app.services.report_service import ReportService

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
)


@router.post("/export", response_model=List[ReportResponse])
async def export_reports(
    request: ReportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_db),
):
    """
    Generate reports for a farm in requested formats.

    ## Request Body
    - **farm_id**: ID of farm to generate reports for
    - **start_date**: Start of data date range (YYYY-MM-DD)
    - **end_date**: End of data date range (YYYY-MM-DD)
    - **report_types**: List of formats to generate: 'pdf', 'csv', 'geojson'
    - **include_charts**: Include charts in PDF (default: true)

    ## Response
    Returns list of ReportResponse objects with download URLs for generated reports.

    ## Reports Generated
    - **PDF**: Multi-page comprehensive report with charts, methodology, and verification
    - **CSV**: Multiple CSV files (NDVI, carbon, LULC, environmental combined)
    - **GeoJSON**: Farm boundary GeoJSON with carbon/NDVI/LULC properties

    ## Error Codes
    - 404: Farm not found or user lacks access
    - 404: No data available for requested date range
    - 400: Invalid date range or parameters
    - 500: Report generation failed
    """
    try:
        # Verify farm exists and user has access
        farm_result = await db.execute(
            select(Farm).where(
                and_(
                    Farm.id == request.farm_id,
                    Farm.company_id == current_user.company_id,
                    Farm.is_active == True,
                )
            )
        )
        farm = farm_result.scalar_one_or_none()

        if not farm:
            raise HTTPException(status_code=404, detail="Farm not found")

        # Parse dates
        start_date = datetime.strptime(request.start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(request.end_date, "%Y-%m-%d").date()

        # Generate reports
        generated_files = await ReportService.generate_reports(
            db=db,
            farm_id=farm.id,
            start_date=start_date,
            end_date=end_date,
            report_types=request.report_types,
            include_charts=request.include_charts,
        )

        # Create database records for generated reports
        report_objects = []

        for report_type in request.report_types:
            if report_type == "pdf":
                file_path = generated_files.get("pdf")
                if file_path:
                    report = Report(
                        farm_id=farm.id,
                        report_type=report_type,
                        file_path=file_path,
                        file_url="",  # Will update after flush
                        start_date=start_date,
                        end_date=end_date,
                        status=ReportStatus.COMPLETED.value,
                        metadata={
                            "include_charts": request.include_charts,
                            "generation_timestamp": timestamp,
                        },
                        file_size=Path(file_path).stat().st_size if Path(file_path).exists() else 0,
                    )
                    db.add(report)
                    report_objects.append(report)

            elif report_type == "csv":
                csv_files = generated_files.get("csv", {})
                for csv_type, file_path in csv_files.items():
                    if file_path:
                        report = Report(
                            farm_id=farm.id,
                            report_type="csv",
                            file_path=file_path,
                            file_url="",  # Will update after flush
                            start_date=start_date,
                            end_date=end_date,
                            status=ReportStatus.COMPLETED.value,
                            metadata={
                                "csv_type": csv_type,
                                "generation_timestamp": timestamp,
                            },
                            file_size=Path(file_path).stat().st_size if Path(file_path).exists() else 0,
                        )
                        db.add(report)
                        report_objects.append(report)

            elif report_type == "geojson":
                file_path = generated_files.get("geojson")
                if file_path:
                    report = Report(
                        farm_id=farm.id,
                        report_type="geojson",
                        file_path=file_path,
                        file_url="",  # Will update after flush
                        start_date=start_date,
                        end_date=end_date,
                        status=ReportStatus.COMPLETED.value,
                        metadata={"generation_timestamp": timestamp},
                        file_size=Path(file_path).stat().st_size if Path(file_path).exists() else 0,
                    )
                    db.add(report)
                    report_objects.append(report)

        # Flush to persist records and assign IDs
        await db.flush()

        # Build responses with persisted IDs and proper download URLs
        responses = []
        for report in report_objects:
            # Update file_url to point to the API download endpoint
            report.file_url = f"/api/v1/reports/{report.id}/download"
            
            csv_type_suffix = ""
            if report.report_type == "csv" and report.metadata and "csv_type" in report.metadata:
                csv_type_suffix = f"_{report.metadata['csv_type']}"

            responses.append(
                ReportResponse(
                    report_id=report.id,
                    farm_id=report.farm_id,
                    farm_name=farm.name,
                    report_type=f"{report.report_type}{csv_type_suffix}",
                    file_url=report.file_url,
                    download_url=f"{settings.REPORTS_BASE_URL}{report.file_url}",
                    status=report.status,
                    file_size=report.file_size,
                    start_date=report.start_date.isoformat(),
                    end_date=report.end_date.isoformat(),
                    created_at=report.created_at.isoformat(),
                )
            )

        await db.commit()

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_db),
):
    """
    Retrieve report metadata by ID.

    Returns report details including file URL and status.
    Validates user has access to the farm the report covers.
    """
    result = await db.execute(
        select(Report).where(Report.id == report_id)
    )
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    # Verify farm access
    farm_result = await db.execute(
        select(Farm).where(
            and_(
                Farm.id == report.farm_id,
                Farm.company_id == current_user.company_id,
            )
        )
    )
    farm = farm_result.scalar_one_or_none()

    if not farm:
        raise HTTPException(status_code=403, detail="Access denied")

    return ReportResponse(
        report_id=report.id,
        farm_id=report.farm_id,
        farm_name=farm.name,
        report_type=report.report_type,
        file_url=report.file_url,
        download_url=f"{settings.REPORTS_BASE_URL}{report.file_url}",
        status=report.status,
        file_size=report.file_size,
        start_date=report.start_date.isoformat(),
        end_date=report.end_date.isoformat(),
        created_at=report.created_at.isoformat(),
    )


@router.get("/{report_id}/download")
async def download_report(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_db),
):
    """
    Download report file.

    Returns the file with appropriate content-type header.
    Validates user has access before serving.
    """
    result = await db.execute(
        select(Report).where(Report.id == report_id)
    )
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    # Verify farm access
    farm_result = await db.execute(
        select(Farm).where(
            and_(
                Farm.id == report.farm_id,
                Farm.company_id == current_user.company_id,
            )
        )
    )
    farm = farm_result.scalar_one_or_none()

    if not farm:
        raise HTTPException(status_code=403, detail="Access denied")

    # Verify file exists
    file_path = Path(report.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    # Determine content type
    content_type = "application/octet-stream"
    if report.report_type == "pdf":
        content_type = "application/pdf"
    elif "csv" in report.report_type:
        content_type = "text/csv"
    elif report.report_type == "geojson":
        content_type = "application/geo+json"

    return FileResponse(
        path=file_path,
        media_type=content_type,
        filename=file_path.name,
    )


@router.get("/farm/{farm_id}/list", response_model=ReportListResponse)
async def list_farm_reports(
    farm_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_db),
):
    """
    List all reports for a specific farm.

    Supports pagination with skip and limit parameters.
    Returns reports in reverse chronological order (newest first).
    """
    # Verify farm access
    farm_result = await db.execute(
        select(Farm).where(
            and_(
                Farm.id == farm_id,
                Farm.company_id == current_user.company_id,
                Farm.is_active == True,
            )
        )
    )
    farm = farm_result.scalar_one_or_none()

    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    # Query reports
    total_result = await db.execute(
        select(Report).where(Report.farm_id == farm_id)
    )
    total = len(total_result.scalars().all())

    result = await db.execute(
        select(Report)
        .where(Report.farm_id == farm_id)
        .order_by(Report.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    reports = result.scalars().all()

    responses = [
        ReportResponse(
            report_id=r.id,
            farm_id=r.farm_id,
            farm_name=farm.name,
            report_type=r.report_type,
            file_url=r.file_url,
            download_url=f"{settings.REPORTS_BASE_URL}{r.file_url}",
            status=r.status,
            file_size=r.file_size,
            start_date=r.start_date.isoformat(),
            end_date=r.end_date.isoformat(),
            created_at=r.created_at.isoformat(),
        )
        for r in reports
    ]

    return ReportListResponse(
        reports=responses,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.delete("/{report_id}")
async def delete_report(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_db),
):
    """
    Delete a report.

    Soft deletes the report record (sets status to 'deleted').
    Physical file is retained for audit purposes.
    """
    result = await db.execute(
        select(Report).where(Report.id == report_id)
    )
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    # Verify farm access
    farm_result = await db.execute(
        select(Farm).where(
            and_(
                Farm.id == report.farm_id,
                Farm.company_id == current_user.company_id,
            )
        )
    )
    farm = farm_result.scalar_one_or_none()

    if not farm:
        raise HTTPException(status_code=403, detail="Access denied")

    # Soft delete
    report.status = ReportStatus.DELETED.value
    await db.commit()

    return {"message": "Report deleted successfully"}
