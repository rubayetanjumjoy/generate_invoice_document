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
    request.session["invoice_context"] = context

    # Render the HTML template with the context data
    return render(request, "invoice.html", context)


from django.http import HttpResponse
from django.core.mail import EmailMessage
from django.conf import settings
from xhtml2pdf import pisa
from bs4 import BeautifulSoup
from django.contrib.auth.decorators import login_required


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

    # Create a Django response object with appropriate PDF headers
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'filename="invoice.pdf"'

    # Create a PDF from the modified HTML content
    pisa_status = pisa.CreatePDF(modified_html, dest=response)

    if pisa_status.err:
        return HttpResponse("Error generating PDF", content_type="text/plain")

    # Get the user's email (you should obtain this value from your authentication or user model)
    user_email = context["email"]  # Replace with the user's email

    # Send the PDF as an attachment via email
    email = EmailMessage(
        "Your Invoice",
        "Please find your invoice attached.",
        settings.EMAIL_HOST_USER,
        [user_email],
    )
    email.attach("invoice.pdf", response.content, "application/pdf")
    email.send()

    return response
