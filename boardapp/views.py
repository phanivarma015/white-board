# views.py

from django.shortcuts import render, redirect, get_object_or_404
import uuid
from .models import Customer, Meeting
from .forms import CustomerForms
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


# ---------------- LOGIN ----------------
def login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = Customer.objects.get(email=email, password=password)
            request.session["email"] = user.email
            return redirect("home")
        except Customer.DoesNotExist:
            return render(request, "login.html", {"msg": "Invalid credentials"})

    return render(request, "login.html")


# ---------------- SIGNUP ----------------
def signup(request):
    if request.method == "POST":
        form = CustomerForms(request.POST)

        if form.is_valid():
            if Customer.objects.filter(email=form.cleaned_data["email"]).exists():
                return render(request, "signup.html", {"msg": "Email already exists"})

            form.save()
            return redirect("login")

        return render(request, "signup.html", {"msg": "Invalid data"})

    return render(request, "signup.html")


# ---------------- HOME ----------------
def home(request):
    if "email" not in request.session:
        return redirect("login")

    current_user = Customer.objects.get(email=request.session["email"])

    query = request.GET.get("search")

    if query:
        users = Customer.objects.filter(
            email__icontains=query
        ).exclude(email=current_user.email)
    else:
        users = Customer.objects.exclude(email=current_user.email)

    my_meetings = Meeting.objects.filter(
        participants=current_user
    ).distinct()

    return render(request, "home.html", {
        "users": users,
        "my_meetings": my_meetings,
        "query": query,
        "current_user": current_user
    })


# ---------------- CREATE MEETING ----------------
def create_meeting(request):
    if "email" not in request.session:
        return redirect("login")

    if request.method == "POST":
        selected_users = request.POST.getlist("selected_users")

        if not selected_users:
            return redirect("home")

        current_user = Customer.objects.get(email=request.session["email"])

        room_name = str(uuid.uuid4()).replace("-", "")[:10]

        meeting = Meeting.objects.create(
            room_name=room_name,
            created_by=current_user
        )

        participants = Customer.objects.filter(id__in=selected_users)

        meeting.participants.set(participants)
        meeting.participants.add(current_user)

        # 🔥 Send real-time invite notification
        channel_layer = get_channel_layer()

        for user in participants:
            async_to_sync(channel_layer.group_send)(
                f"user_{user.id}",
                {
                    "type": "send_notification",
                    "room_name": room_name
                }
            )

        return redirect("meeting_room", room_name=room_name)

    return redirect("home")


# ---------------- MEETING ROOM ----------------
def meeting_room(request, room_name):
    if "email" not in request.session:
        return redirect("login")

    current_user = Customer.objects.get(email=request.session["email"])

    meeting = get_object_or_404(Meeting, room_name=room_name)

    # Restrict access only to participants
    if current_user not in meeting.participants.all():
        return redirect("home")

    return render(request, "create_meeting.html", {
        "room_name": room_name,
        "current_user": current_user
    })


# ---------------- DELETE MEETING ----------------
def delete_meeting(request, room_name):
    if "email" not in request.session:
        return redirect("login")

    current_user = Customer.objects.get(email=request.session["email"])
    meeting = get_object_or_404(Meeting, room_name=room_name)

    # Only meeting creator can delete
    if meeting.created_by == current_user:
        meeting.delete()

    return redirect("home")