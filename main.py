
import smtplib
import sys
import mimetypes
from email.message import EmailMessage
from email.utils import parseaddr
from getpass import getpass
from pathlib import Path


MAX_SUBJECT_LENGTH = 200
MAX_BODY_LENGTH = 100_000
MAX_RECIPIENTS = 100


def get_recipients():
    print("\nHOW WOULD YOU LIKE TO PROVIDE RECIPIENTS?")
    print("1. Enter email addresses manually")
    print("2. Load email addresses from a file")

    while True:
        choice = input("\nYour choice: ").strip()

        if choice == "1":
            print("\nEnter email addresses separated by commas.")
            addresses = input("Recipients: ").split(",")

        elif choice == "2":
            filename = input("Enter the file path: ").strip()

            try:
                addresses = Path(filename).read_text(
                    encoding="utf-8"
                ).splitlines()

            except FileNotFoundError:
                print("File not found. Try again.")
                continue

            except OSError as error:
                print(f"Could not read file: {error}")
                continue

        else:
            print("Invalid choice. Choose 1 or 2.")
            continue

        # Remove whitespace and empty lines
        addresses = [address.strip() for address in addresses]
        addresses = [address for address in addresses if address]

        # Validate email addresses
        valid_addresses = []

        for address in addresses:
            parsed = parseaddr(address)[1]

            if (
                parsed == address
                and "@" in address
                and "." in address.split("@")[-1]
            ):
                valid_addresses.append(address)
            else:
                print(f"Invalid email address: {address}")

        # Remove duplicates while preserving order
        valid_addresses = list(dict.fromkeys(valid_addresses))

        if len(valid_addresses) > MAX_RECIPIENTS:
            print(f"Maximum {MAX_RECIPIENTS} recipients allowed.")
            continue

        if valid_addresses:
            return valid_addresses

        print("No valid email addresses found. Try again.")


def get_email_body():
    print("\nEnter your email message.")
    print("You can use multiple lines and paragraphs.")
    print("Type END on a separate line when you finish.\n")

    body_lines = []

    for line in sys.stdin:
        if line.strip() == "END":
            break

        body_lines.append(line)

    return "".join(body_lines)


def get_email_content():
    print("\nHOW WOULD YOU LIKE TO PROVIDE EMAIL CONTENT?")
    print("1. Enter subject and message manually")
    print("2. Load subject and message from a file")

    while True:
        choice = input("\nYour choice: ").strip()

        if choice == "1":
            subject = input("\nEnter the email subject: ")
            body = get_email_body()

        elif choice == "2":
            print("\nEMAIL FILE FORMAT")
            print("-" * 50)
            print("""
Your text file must follow this structure:

First line: Email subject

Leave one blank line.

Everything after the blank line is the email message.

Example:

Application for available position

Hello,

I am contacting you regarding your job advertisement.

I would like to apply for the available position.

Thank you for your time.

Best regards,
John

IMPORTANT:
- The subject must be on the first line.
- Leave a blank line between the subject and message.
- The message can contain multiple paragraphs.
- Maximum subject length: 200 characters.
- Maximum message length: 100,000 characters.
- Save the file as .txt using UTF-8 encoding.
""")
            print("-" * 50)

            filename = input("\nEnter the file path: ").strip()

            try:
                content = Path(filename).read_text(
                    encoding="utf-8"
                )

                content = content.replace("\r\n", "\n")

                subject, separator, body = content.partition("\n\n")

                if not separator:
                    print("Invalid file format.")
                    print("Separate the subject and body with a blank line.")
                    continue

                subject = subject.strip()
                body = body.strip()

            except FileNotFoundError:
                print("File not found. Try again.")
                continue

            except OSError as error:
                print(f"Could not read file: {error}")
                continue

        else:
            print("Invalid choice. Choose 1 or 2.")
            continue

        # Validate subject
        if not subject:
            print("Subject cannot be empty.")
            continue

        if len(subject) > MAX_SUBJECT_LENGTH:
            print(
                f"Subject is too long. Maximum: "
                f"{MAX_SUBJECT_LENGTH} characters."
            )
            continue

        # Validate body
        if not body.strip():
            print("Email message cannot be empty.")
            continue

        if len(body) > MAX_BODY_LENGTH:
            print(
                f"Message is too long. Maximum: "
                f"{MAX_BODY_LENGTH:,} characters."
            )
            continue

        return subject, body


def get_attachments():
    attachments = []

    print("\nFILE ATTACHMENTS")
    print("You can attach multiple files to your emails.")
    print("For example: PDF, images, Word documents, etc.")

    while True:
        choice = input("\nAdd an attachment? (yes/no): ").strip().lower()

        if choice in ("no", "n"):
            return attachments

        if choice not in ("yes", "y"):
            print("Invalid choice. Enter yes or no.")
            continue

        filename = input("Enter the file path: ").strip()

        try:
            file_path = Path(filename).expanduser()

            if not file_path.is_file():
                print("The specified file does not exist.")
                continue

            file_data = file_path.read_bytes()

            # Detect the file's MIME type
            content_type, encoding = mimetypes.guess_type(
                file_path.name
            )

            if content_type is None or encoding is not None:
                content_type = "application/octet-stream"

            maintype, subtype = content_type.split("/", 1)

            attachments.append(
                (
                    file_path.name,
                    file_data,
                    maintype,
                    subtype
                )
            )

            print(f"Added attachment: {file_path.name}")

        except OSError as error:
            print(f"Could not read file: {error}")
            continue

        print("\n1. Add another attachment")
        print("2. Finish adding attachments")

        next_choice = input("Your choice: ").strip()

        if next_choice == "2":
            return attachments

        if next_choice != "1":
            print("Invalid choice. Returning to attachment selection.")
            continue


def main():
    print("=" * 50)
    print("          PYTHON GMAIL SMTP EMAIL SENDER")
    print("=" * 50)

    print("""
GMAIL AUTHENTICATION

To send emails using Gmail, you need a Google App Password.

IMPORTANT:
- Do NOT enter your regular Google account password.
- You must generate a separate App Password.

HOW TO GENERATE YOUR APP PASSWORD:

1. Open: https://myaccount.google.com/apppasswords
2. Sign in to your Google account if requested.
3. Enter a name for the application (e.g. Python Email Sender).
4. Click Create.
5. Google will generate a 16-character App Password.

Copy that password and enter it below.

Note: App Passwords may not be available for some
Google accounts.
""")

    print("=" * 50)

    sender = input("\nEnter your Gmail address: ").strip()
    password = getpass("Enter your Google App Password: ")

    recipients = get_recipients()

    print(f"\nFound {len(recipients)} valid recipient(s).")

    subject, body = get_email_content()

    attachments = get_attachments()

    # Confirm before sending
    print("\nEMAIL SUMMARY")
    print("-" * 50)
    print(f"Sender: {sender}")
    print(f"Recipients: {len(recipients)}")
    print(f"Subject: {subject}")
    print(f"Message length: {len(body):,} characters")
    print(f"Attachments: {len(attachments)}")

    if attachments:
        print("\nATTACHED FILES:")

        for filename, file_data, maintype, subtype in attachments:
            print(f"- {filename} ({len(file_data):,} bytes)")

    print("-" * 50)

    confirmation = input("Send emails? (yes/no): ").strip().lower()

    if confirmation not in ("yes", "y"):
        print("Sending cancelled.")
        return

    # Connect to Gmail
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender, password)

            for recipient in recipients:
                msg = EmailMessage()
                msg["Subject"] = subject
                msg["From"] = sender
                msg["To"] = recipient
                msg.set_content(body)

                # Add attachments to the email
                for filename, file_data, maintype, subtype in attachments:
                    msg.add_attachment(
                        file_data,
                        maintype=maintype,
                        subtype=subtype,
                        filename=filename
                    )

                try:
                    smtp.send_message(msg)
                    print(f"Successfully sent to: {recipient}")

                except Exception as error:
                    print(f"Failed to send to {recipient}: {error}")

        print("\nFinished sending emails!")

    except smtplib.SMTPAuthenticationError:
        print("\nAuthentication failed!")
        print("Check your Gmail address and App Password.")

    except Exception as error:
        print(f"\nAn error occurred: {error}")


if __name__ == "__main__":
    main()
