# Import the modules
import requests
from bs4 import BeautifulSoup
from datetime import date, datetime, timedelta

import asyncio
import os
import datetime as dt

from fastapi import Depends, FastAPI
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from settings import get_settings, DevSettings, ProdSettings
from precipitation import PrecipitationData
from apscheduler.schedulers.background import BackgroundScheduler

# Import the logging configuration module
from logging_config import get_logger

logger = get_logger(__name__)

app = FastAPI()

# Define the scheduler
scheduler = BackgroundScheduler()

reports = [
    {
        "name": "Capesize and Panamax FFA report",
        "url": "https://fisapp.com/wp-content/uploads/2023/09/CapePMX-Report-050923.pdf",
    },
    {
        "name": "London Iron Ore Derivatives report",
        "url": "https://fisapp.com/wp-content/uploads/2023/09/FIS-Iron-Ore-London-Report-05092023.pdf",
    },
    {
        "name": "Capesize Technical Report",
        "url": "https://fisapp.com/wp-content/uploads/2023/09/FIS-CAPESIZE-4-PAGE-TECHNICAL-REPORT-04-09-23.pdf",
    },
]


# Add the scheduler's start and stop methods to the startup and shutdown events of FastAPI
@app.on_event("startup")
async def startup_event():
    settings = get_settings()
    scheduler.configure(timezone=settings.SCHEDULER_TIMEZONE)
    if settings.SCHEDULER_TYPE == "cron":
        scheduler.add_job(
            prepare_fis_rpt,
            settings.SCHEDULER_TYPE,
            hour=settings.SCHEDULER_HOUR,
            minute=settings.SCHEDULER_MINUTE,
            misfire_grace_time=settings.MISFIRE_GRACE_TIME,
            args=[settings],
        )
    else:
        scheduler.add_job(
            prepare_fis_rpt,
            settings.SCHEDULER_TYPE,
            hours=settings.SCHEDULER_INT_HOURS,
            minutes=settings.SCHEDULER_INT_MINUTES,
            misfire_grace_time=settings.MISFIRE_GRACE_TIME,
            args=[settings],
        )

    scheduler.start()
    print("Scheduler started")


@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()
    print("Scheduler stopped")


def prepare_fis_rpt(settings: (DevSettings | ProdSettings | None)):
    base_url = settings.FIS_BASE_URL

    # Enter the desired current_date in YYYY-MM-DD format
    desired_date_str = "2023-05-31"

    # Convert the desired_date_str to a datetime object
    report_date = datetime.strptime(desired_date_str, "%Y-%m-%d")

    # Get the current date
    # report_date = date.today()
    report_date -= timedelta(days=1)

    date_str = report_date.strftime(date_format)

    # Construct the full url with the date
    for report_data in reports:
        report = factory.create_report(report_data["name"], report_data["url"])
        report.download()

    fisreport_url = f"{base_url}/{year}/{month}/CapePMX-Report-{date_str}.pdf"

    output_file = os.path.join("data", "precip.csv")
    sub_dir = "data/nc"
    file_name = "precip.2022.nc"
    file_path = os.path.abspath(os.path.join(sub_dir, file_name))

    precip_data = PrecipitationData(fisreport_url, settings)

    curr_time_value = precip_data.get_curr_time_value()
    prev_time_value = precip_data.get_previous_time_value()

    if curr_time_value > prev_time_value:
        precip_data.read_data()

        # mean, median, std_dev = precip_data.compute_statistics()
        # print(f"Mean: {mean}, Median: {median}, Standard Deviation: {std_dev}")

        # subset = precip_data.extract_subset("2023-03-15", "2023-03-20")
        # print(subset)

        precip_data.save_to_csv(output_file)

        file_exists = os.path.exists(output_file)

        if file_exists:
            logger.info(f"Path:{output_file}")

            asyncio.run(
                send_email(
                    settings,
                    "Precipitaion Report",
                    settings.RECIPIENTS,
                    output_file,
                )
            )
        precip_data.update_previous_time_value(curr_time_value)


# Define the base url and the date format
base_url = "https://fisapp.com/wp-content/uploads"
date_format = "%d%m%y"

# Enter the desired current_date in YYYY-MM-DD format
desired_date_str = "2023-05-31"

# Convert the desired_date_str to a datetime object
report_date = datetime.strptime(desired_date_str, "%Y-%m-%d")

# Get the current date
# report_date = date.today()
report_date -= timedelta(days=1)

# Initialize a flag to indicate if there are more files to download
more_files = 10

# Loop until there are no more files or an error occurs
while more_files != 0:
    # Skip downloading if current date is Saturday (5) or Sunday (6)
    if report_date.weekday() not in [5, 6]:
        # Format the date as a string
        date_str = report_date.strftime(date_format)

        year = report_date.year
        month = report_date.strftime("%m")

        # Construct the full url with the date
        full_url = f"{base_url}/{year}/{month}/CapePMX-Report-{date_str}.pdf"

        # Try to get the response from the url
        try:
            response = requests.get(full_url)

            # Check if the response status code is 200 (OK)
            if response.status_code == 200:
                more_files = 10
                # File found, download it
                file_name = f"CapePMX-Report-{date_str}.pdf"
                with open(file_name, "wb") as f:
                    f.write(response.content)

                # Print a message to indicate the file is downloaded
                print(f"Downloaded {file_name} from {full_url}")

            # If the response status code is not 200, stop the loop
            else:
                more_files = more_files - 1

        # If an exception occurs, stop the loop and print the error message
        except Exception as e:
            more_files = False
            print(f"An error occurred: {e}")
    # Subtract one day from the date
    report_date -= timedelta(days=1)


async def send_email(
    settings: (DevSettings | ProdSettings | None), subject, email_to, file
):
    message = MessageSchema(
        subject=subject,
        recipients=email_to,
        body="",
        attachments=[{"file": file}],
        subtype=MessageType.html,
    )

    conf = ConnectionConfig(
        MAIL_USERNAME=settings.MAIL_USERNAME,
        MAIL_PASSWORD=settings.MAIL_PASSWORD.get_secret_value(),
        MAIL_FROM=settings.MAIL_FROM,
        MAIL_PORT=settings.MAIL_PORT,
        MAIL_SERVER=settings.MAIL_SERVER,
        MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
        MAIL_STARTTLS=True,
        MAIL_SSL_TLS=False,
        USE_CREDENTIALS=True,
        TEMPLATE_FOLDER="./templates/",
    )
    fm = FastMail(conf)
    try:
        response = await fm.send_message(message)
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
    else:
        logger.info(f"Email sent successfully: {response}")


@app.get("/info")
async def info(settings: (DevSettings | ProdSettings | None) = Depends(get_settings)):
    logger.info(f"Setting: {settings}")
    prepare_fis_rpt(settings=settings)
    return {"message": "Email sent!"}


@app.get("/")
async def root():
    return {"msg": "Hello World"}
