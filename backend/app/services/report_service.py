"""Service for generating reports in multiple formats."""

import os
from datetime import datetime, date as date_type
from pathlib import Path
from typing import Optional, List, Dict, Any
import json

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from fpdf import FPDF
import pandas as pd
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.farm import Farm
from app.models.measurement import Measurement
from app.models.report import Report, ReportStatus, ReportType
from app.core.config import settings


class ReportService:
    """Service for generating and managing reports."""

    @staticmethod
    def _ensure_report_dirs() -> None:
        """Ensure report directories exist."""
        base_dir = Path(settings.REPORTS_DIR)
        for subdir in ["pdf", "csv", "geojson"]:
            (base_dir / subdir).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _generate_filename(farm_id: int, report_type: str, timestamp: Optional[str] = None) -> str:
        """Generate unique filename for report."""
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"farm_{farm_id}_{report_type}_{timestamp}"

    @staticmethod
    async def _fetch_farm_data(db: AsyncSession, farm_id: int) -> Optional[Farm]:
        """Fetch farm data from database."""
        result = await db.execute(
            select(Farm).where(Farm.id == farm_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def _fetch_measurements(
        db: AsyncSession,
        farm_id: int,
        start_date: date_type,
        end_date: date_type,
        measurement_type: Optional[str] = None,
    ) -> List[Measurement]:
        """Fetch measurements for a farm within date range."""
        query = select(Measurement).where(
            and_(
                Measurement.farm_id == farm_id,
                Measurement.measurement_date >= start_date,
                Measurement.measurement_date <= end_date,
            )
        )
        if measurement_type:
            query = query.where(Measurement.measurement_type == measurement_type)

        result = await db.execute(query.order_by(Measurement.measurement_date))
        return result.scalars().all()

    @staticmethod
    def create_ndvi_timeseries_chart(
        measurements: List[Measurement],
        output_path: str,
    ) -> None:
        """Create NDVI time-series chart with error bars."""
        if not measurements:
            return

        dates = [m.measurement_date for m in measurements]
        values = [m.value for m in measurements]
        std_devs = [m.std_dev or 0 for m in measurements]

        plt.figure(figsize=(12, 6))
        plt.errorbar(dates, values, yerr=std_devs, marker="o", linestyle="-", capsize=5)
        plt.xlabel("Date")
        plt.ylabel("NDVI Value")
        plt.title("NDVI Time Series")
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close()

    @staticmethod
    def create_carbon_chart(
        measurements: List[Measurement],
        output_path: str,
    ) -> None:
        """Create carbon accumulation chart with confidence intervals."""
        if not measurements:
            return

        dates = [m.measurement_date for m in measurements]
        co2_values = [m.value for m in measurements]  # value = co2_total_tonnes
        
        # Extract confidence intervals from metadata
        ci_lowers = []
        ci_uppers = []
        for m in measurements:
            if m.meta:
                ci_lowers.append(m.meta.get("confidence_interval_lower", m.value))
                ci_uppers.append(m.meta.get("confidence_interval_upper", m.value))
            else:
                ci_lowers.append(m.value)
                ci_uppers.append(m.value)

        plt.figure(figsize=(12, 6))
        plt.plot(dates, co2_values, marker="o", linestyle="-", label="CO2 Estimate", linewidth=2)
        plt.fill_between(dates, ci_lowers, ci_uppers, alpha=0.3, label="95% Confidence Interval")
        plt.xlabel("Date")
        plt.ylabel("CO2 (tonnes)")
        plt.title("Carbon Accumulation with Confidence Intervals")
        plt.legend()
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close()

    @staticmethod
    def create_lulc_pie_chart(
        lulc_measurements: List[Measurement],
        output_path: str,
    ) -> None:
        """Create pie chart for LULC distribution."""
        if not lulc_measurements:
            return

        # Aggregate LULC data from most recent measurement
        latest_lulc = lulc_measurements[0] if lulc_measurements else None
        if not latest_lulc or not latest_lulc.meta:
            return

        classes = latest_lulc.meta.get("classes", [])
        if not classes:
            return

        labels = [c.get("name") for c in classes]
        sizes = [c.get("percentage", 0) for c in classes]

        plt.figure(figsize=(10, 8))
        plt.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
        plt.title("Land Use/Land Cover Distribution")
        plt.axis("equal")
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close()

    @staticmethod
    def generate_verification_summary(measurements: List[Measurement]) -> Dict[str, Any]:
        """Generate verification summary with methodology and confidence metrics."""
        if not measurements:
            return {}

        # Get metadata from most recent measurement
        metadata = {}
        for m in measurements:
            if m.meta:
                metadata = m.meta
                break

        # Calculate average confidence
        confidence_scores = []
        std_devs = []
        for m in measurements:
            if m.meta:
                if "confidence_score" in m.meta:
                    confidence_scores.append(m.meta["confidence_score"])
                if "std_dev" in m.meta:
                    std_devs.append(m.meta["std_dev"])

        summary = {
            "methodology": metadata.get("methodology", "IPCC Tier 2"),
            "uncertainty_method": metadata.get("uncertainty_method", "Monte Carlo"),
            "monte_carlo_iterations": metadata.get("monte_carlo_iterations", 10000),
            "land_use_classes_used": metadata.get("land_use_class"),
            "data_sources": ["Sentinel-2 NDVI", "Dynamic World LULC"],
            "average_confidence_score": (
                sum(confidence_scores) / len(confidence_scores) if confidence_scores else None
            ),
            "average_std_dev": (
                sum(std_devs) / len(std_devs) if std_devs else None
            ),
            "generation_timestamp": datetime.now().isoformat(),
        }
        return summary

    @staticmethod
    async def generate_pdf_report(
        db: AsyncSession,
        farm: Farm,
        measurements_ndvi: List[Measurement],
        measurements_carbon: List[Measurement],
        measurements_lulc: List[Measurement],
        include_charts: bool = True,
    ) -> str:
        """Generate comprehensive PDF report."""
        ReportService._ensure_report_dirs()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = ReportService._generate_filename(farm.id, "pdf", timestamp)
        pdf_path = Path(settings.REPORTS_DIR) / "pdf" / f"{filename}.pdf"

        # Create PDF
        pdf = FPDF()
        pdf.add_page()

        # Page 1: Cover
        pdf.set_font("Arial", "B", 24)
        pdf.cell(0, 20, "Carbon Assessment Report", ln=True, align="C")
        pdf.set_font("Arial", "", 14)
        pdf.cell(0, 10, farm.name, ln=True, align="C")
        pdf.cell(0, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="C")

        # Page 2: Executive Summary
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Executive Summary", ln=True)

        pdf.set_font("Arial", "", 11)
        if measurements_carbon:
            total_co2 = sum(m.value for m in measurements_carbon)
            avg_confidence = sum(
                m.meta.get("confidence_score", 0) for m in measurements_carbon if m.meta
            ) / len(measurements_carbon)
            
            pdf.cell(0, 10, f"Farm: {farm.name}", ln=True)
            pdf.cell(0, 10, f"Area: {farm.area_ha} hectares", ln=True)
            pdf.cell(0, 10, f"Total CO2 Estimate: {total_co2:.2f} tonnes", ln=True)
            pdf.cell(0, 10, f"Average Confidence Score: {avg_confidence:.1f}/100", ln=True)

        # Page 3: Methodology
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Methodology", ln=True)

        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(
            0,
            5,
            "This report uses IPCC Tier 2 methodology with stochastic uncertainty "
            "quantification via Monte Carlo simulation (10,000 iterations). "
            "Allometric equations from Chave et al. (2014) are used with land-use-specific "
            "parameters from Dynamic World classification. "
            "Confidence intervals represent the 95% range of estimated values. "
            "NDVI data sourced from Sentinel-2 satellite imagery.",
        )

        # Page 4-5: Charts (if include_charts)
        if include_charts and measurements_ndvi:
            # Create charts
            ndvi_chart = Path(settings.REPORTS_DIR) / "pdf" / f"ndvi_{timestamp}.png"
            carbon_chart = Path(settings.REPORTS_DIR) / "pdf" / f"carbon_{timestamp}.png"
            lulc_chart = Path(settings.REPORTS_DIR) / "pdf" / f"lulc_{timestamp}.png"

            ReportService.create_ndvi_timeseries_chart(measurements_ndvi, str(ndvi_chart))
            ReportService.create_carbon_chart(measurements_carbon, str(carbon_chart))
            if measurements_lulc:
                ReportService.create_lulc_pie_chart(measurements_lulc, str(lulc_chart))

            # Add charts to PDF
            if ndvi_chart.exists():
                pdf.add_page()
                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, "NDVI Time Series", ln=True)
                pdf.image(str(ndvi_chart), x=10, y=30, w=190)

            if carbon_chart.exists():
                pdf.add_page()
                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, "Carbon Accumulation", ln=True)
                pdf.image(str(carbon_chart), x=10, y=30, w=190)

            if lulc_chart.exists():
                pdf.add_page()
                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, "Land Use/Land Cover Distribution", ln=True)
                pdf.image(str(lulc_chart), x=10, y=30, w=190)

        # Page 6: Verification Summary
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Verification Summary", ln=True)

        pdf.set_font("Arial", "", 11)
        summary = ReportService.generate_verification_summary(measurements_carbon)
        pdf.cell(0, 10, f"Average Confidence Score: {summary.get('average_confidence_score', 'N/A')}", ln=True)
        pdf.cell(0, 10, f"Average Std Dev: {summary.get('average_std_dev', 'N/A')}", ln=True)
        pdf.cell(0, 10, f"Data Sources: {', '.join(summary.get('data_sources', []))}", ln=True)

        # Save PDF
        pdf.output(str(pdf_path))
        return str(pdf_path)

    @staticmethod
    async def generate_csv_ndvi(
        measurements: List[Measurement],
        farm: Farm,
    ) -> str:
        """Generate CSV export of NDVI time-series."""
        ReportService._ensure_report_dirs()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = ReportService._generate_filename(farm.id, "csv_ndvi", timestamp)
        csv_path = Path(settings.REPORTS_DIR) / "csv" / f"{filename}.csv"

        data = {
            "date": [m.measurement_date.isoformat() for m in measurements],
            "ndvi": [m.value for m in measurements],
            "std_dev": [m.std_dev for m in measurements],
            "farm_id": [farm.id] * len(measurements),
            "farm_name": [farm.name] * len(measurements),
        }

        df = pd.DataFrame(data)
        df.to_csv(csv_path, index=False)
        return str(csv_path)

    @staticmethod
    async def generate_csv_carbon(
        measurements: List[Measurement],
        farm: Farm,
    ) -> str:
        """Generate CSV export of carbon estimates."""
        ReportService._ensure_report_dirs()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = ReportService._generate_filename(farm.id, "csv_carbon", timestamp)
        csv_path = Path(settings.REPORTS_DIR) / "csv" / f"{filename}.csv"

        data = {
            "date": [m.measurement_date.isoformat() for m in measurements],
            "ndvi": [],
            "agb_tonnes_ha": [],
            "carbon_tonnes_ha": [],
            "co2_tonnes_ha": [],
            "confidence_score": [],
            "ci_lower": [],
            "ci_upper": [],
            "std_dev": [],
        }

        for m in measurements:
            if m.meta:
                data["ndvi"].append(m.meta.get("ndvi"))
                data["agb_tonnes_ha"].append(m.meta.get("agb_tonnes", 0) / farm.area_ha)
                data["carbon_tonnes_ha"].append(m.meta.get("carbon_tonnes", 0) / farm.area_ha)
                data["co2_tonnes_ha"].append(m.value / farm.area_ha)
                data["confidence_score"].append(m.meta.get("confidence_score"))
                data["ci_lower"].append(m.meta.get("confidence_interval_lower"))
                data["ci_upper"].append(m.meta.get("confidence_interval_upper"))
                data["std_dev"].append(m.std_dev)
            else:
                data["ndvi"].append(None)
                data["agb_tonnes_ha"].append(None)
                data["carbon_tonnes_ha"].append(None)
                data["co2_tonnes_ha"].append(m.value / farm.area_ha)
                data["confidence_score"].append(None)
                data["ci_lower"].append(None)
                data["ci_upper"].append(None)
                data["std_dev"].append(m.std_dev)

        df = pd.DataFrame(data)
        df.to_csv(csv_path, index=False)
        return str(csv_path)

    @staticmethod
    async def generate_csv_lulc(
        measurements: List[Measurement],
        farm: Farm,
    ) -> str:
        """Generate CSV export of LULC classification."""
        ReportService._ensure_report_dirs()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = ReportService._generate_filename(farm.id, "csv_lulc", timestamp)
        csv_path = Path(settings.REPORTS_DIR) / "csv" / f"{filename}.csv"

        rows = []
        for m in measurements:
            if m.meta and "classes" in m.meta:
                for cls in m.meta["classes"]:
                    rows.append({
                        "date": m.measurement_date.isoformat(),
                        "class_id": cls.get("id"),
                        "class_name": cls.get("name"),
                        "area_ha": cls.get("area_ha"),
                        "percentage": cls.get("percentage"),
                    })

        df = pd.DataFrame(rows)
        df.to_csv(csv_path, index=False)
        return str(csv_path)

    @staticmethod
    async def generate_csv_environmental(
        measurements_ndvi: List[Measurement],
        measurements_carbon: List[Measurement],
        measurements_lulc: List[Measurement],
        farm: Farm,
    ) -> str:
        """Generate combined environmental data CSV."""
        ReportService._ensure_report_dirs()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = ReportService._generate_filename(farm.id, "csv_environmental", timestamp)
        csv_path = Path(settings.REPORTS_DIR) / "csv" / f"{filename}.csv"

        # Create unified dataset
        data_by_date = {}

        # NDVI data
        for m in measurements_ndvi:
            date_key = m.measurement_date.isoformat()
            if date_key not in data_by_date:
                data_by_date[date_key] = {"date": date_key}
            data_by_date[date_key]["ndvi"] = m.value

        # Carbon data
        for m in measurements_carbon:
            date_key = m.measurement_date.isoformat()
            if date_key not in data_by_date:
                data_by_date[date_key] = {"date": date_key}
            if m.meta:
                data_by_date[date_key]["co2_tonnes"] = m.value
                data_by_date[date_key]["confidence_score"] = m.meta.get("confidence_score")

        # LULC data
        for m in measurements_lulc:
            date_key = m.measurement_date.isoformat()
            if date_key not in data_by_date:
                data_by_date[date_key] = {"date": date_key}
            if m.meta:
                data_by_date[date_key]["dominant_lulc_class"] = m.meta.get("dominant_class")

        df = pd.DataFrame(list(data_by_date.values()))
        df = df.sort_values("date")
        df.to_csv(csv_path, index=False)
        return str(csv_path)

    @staticmethod
    async def generate_geojson_boundaries(
        farm: Farm,
        measurements_ndvi: List[Measurement],
        measurements_carbon: List[Measurement],
        measurements_lulc: List[Measurement],
    ) -> str:
        """Generate GeoJSON export of farm boundaries with properties."""
        ReportService._ensure_report_dirs()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = ReportService._generate_filename(farm.id, "geojson", timestamp)
        geojson_path = Path(settings.REPORTS_DIR) / "geojson" / f"{filename}.geojson"

        # Calculate summary statistics
        total_carbon = sum(m.value for m in measurements_carbon) if measurements_carbon else 0
        mean_ndvi = sum(m.value for m in measurements_ndvi) / len(measurements_ndvi) if measurements_ndvi else 0
        dominant_lulc = None
        if measurements_lulc:
            latest_lulc = measurements_lulc[0]
            if latest_lulc.meta:
                dominant_lulc = latest_lulc.meta.get("dominant_class")

        # Create GeoJSON feature
        feature = {
            "type": "Feature",
            "geometry": farm.geometry,
            "properties": {
                "farm_id": farm.id,
                "farm_name": farm.name,
                "area_ha": farm.area_ha,
                "total_carbon_tonnes": total_carbon,
                "mean_ndvi": mean_ndvi,
                "dominant_lulc_class": dominant_lulc,
            },
        }

        feature_collection = {
            "type": "FeatureCollection",
            "features": [feature],
        }

        with open(geojson_path, "w") as f:
            json.dump(feature_collection, f, indent=2)

        return str(geojson_path)

    @staticmethod
    async def generate_reports(
        db: AsyncSession,
        farm_id: int,
        start_date: date_type,
        end_date: date_type,
        report_types: List[str],
        include_charts: bool = True,
    ) -> Dict[str, str]:
        """Main method to generate all requested report types."""
        # Fetch farm
        farm = await ReportService._fetch_farm_data(db, farm_id)
        if not farm:
            raise ValueError(f"Farm {farm_id} not found")

        # Fetch measurements
        measurements_ndvi = await ReportService._fetch_measurements(
            db, farm_id, start_date, end_date, "ndvi"
        )
        measurements_carbon = await ReportService._fetch_measurements(
            db, farm_id, start_date, end_date, "carbon"
        )
        measurements_lulc = await ReportService._fetch_measurements(
            db, farm_id, start_date, end_date, "lulc"
        )

        if not measurements_carbon and not measurements_ndvi:
            raise ValueError(f"No measurements found for farm {farm_id} in date range")

        generated_files = {}

        # Generate requested report types
        for report_type in report_types:
            if report_type == "pdf":
                pdf_path = await ReportService.generate_pdf_report(
                    db, farm, measurements_ndvi, measurements_carbon, measurements_lulc, include_charts
                )
                generated_files["pdf"] = pdf_path
            elif report_type == "csv":
                csv_ndvi = await ReportService.generate_csv_ndvi(measurements_ndvi, farm)
                csv_carbon = await ReportService.generate_csv_carbon(measurements_carbon, farm)
                csv_lulc = (
                    await ReportService.generate_csv_lulc(measurements_lulc, farm)
                    if measurements_lulc else None
                )
                csv_env = await ReportService.generate_csv_environmental(
                    measurements_ndvi, measurements_carbon, measurements_lulc, farm
                )
                generated_files["csv"] = {
                    "ndvi": csv_ndvi,
                    "carbon": csv_carbon,
                    "lulc": csv_lulc,
                    "environmental": csv_env,
                }
            elif report_type == "geojson":
                geojson_path = await ReportService.generate_geojson_boundaries(
                    farm, measurements_ndvi, measurements_carbon, measurements_lulc
                )
                generated_files["geojson"] = geojson_path

        return generated_files
