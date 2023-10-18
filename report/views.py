from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from django.template.loader import get_template
from xhtml2pdf import pisa
from bs4 import BeautifulSoup
from django.contrib.auth import logout

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
import pdfkit
from django.core.mail import EmailMessage


def login_view(request):
    if request.user.is_authenticated:
        return redirect("form")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        print(username, password)
        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Log the user in
            login(request, user)
            # Redirect to a success page or home page
            return redirect(
                "form"
            )  # Replace 'home' with the URL name of your home page
        else:
            # Authentication failed, show an error message
            error_message = "Invalid username or password"
            return render(request, "login.html", {"error_message": error_message})

    return render(request, "login.html")


def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect("login")


@login_required
def form(request):
    return render(request, "form.html")


def send_invoice_email(email, pdf_response):
    subject = "Your Invoice"
    message = "Please find your invoice attached."
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]

    email_message = EmailMessage(subject, message, from_email, recipient_list)
    email_message.attach("invoice.pdf", pdf_response.content, "application/pdf")

    # Send the email
    email_message.send()


@login_required
def generate_pdf(request):
    template_path = "invoice.html"

    context = request.session.get("invoice_context", {})

    template = get_template(template_path)
    html = template.render(context)

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    # Remove all elements with the class "action-buttons"
    elements_to_remove = soup.find_all(class_="action-buttons")
    for element in elements_to_remove:
        element.extract()

    # Get the modified HTML content
    modified_html = str(soup)

    # Specify the path to wkhtmltopdf executable (for Windows)
    config = pdfkit.configuration(
        wkhtmltopdf="C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe"
    )

    # Generate the PDF from the HTML content
    pdf = pdfkit.from_string(modified_html, False, configuration=config)

    # Create an HTTP response with the PDF content
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="invoice.pdf"'
    return response


@login_required
def invoice(request):
    context = {}  # Initialize the context dictionary

    if request.method == "POST":
        # Get form data from POST request
        email = request.POST.get("email")
        fare = request.POST.get("fare")
        pickup = request.POST.get("pickup")
        to = request.POST.get("to")
        vehicle = request.POST.get("vehicle")
        payment_method = request.POST.get("payment")

        # Add the form data to the context dictionary
        context["email"] = email
        context["fare"] = fare
        context["pickup"] = pickup
        context["to"] = to
        context["vehicle"] = vehicle
        context["payment_method"] = payment_method

        # Store the context in the session for generating PDF
        request.session["invoice_context"] = context

        # Generate the PDF and attach it to an email
        pdf_response = generate_pdf(request)
        send_invoice_email(email, pdf_response)

    # Render the HTML template with the context data
    return render(request, "invoice.html", context)
