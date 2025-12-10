from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from .models import Location
from .utils import get_lat_lon_from_pincode
from .utils import build_graph
from .utils import a_star


@require_http_methods(["GET", "POST"]) # pyright: ignore[reportUndefinedVariable]
def add_location(request):
    message = ""
    
    if request.method == "POST":
        pincode = request.POST.get("pincode", "").strip()  # Remove extra spaces

        if not pincode:
            message = "Please enter a valid pincode."
        elif Location.objects.filter(pincode=pincode).exists():
            message = "Pincode already saved."
        else:
            try:
                lat, lon = get_lat_lon_from_pincode(pincode)  # Your helper function
                if lat is None or lon is None:
                    message = "Invalid pincode or no data found!"
                else:
                    Location.objects.create(
                        pincode=pincode,
                        latitude=lat,
                        longitude=lon
                    )
                    message = "Pincode added successfully."
            except Exception as e:
                message = f"Error occurred: {str(e)}"

    return render(request, "add_location.html", {"message": message})

def location_list(request):
    loactions = Location.objects.all()
    return render(request, 'locations.html', {'locations':loactions})

def generate_edges(request):
    message = ""
    if request.method == "POST":
        build_graph(k_neighbors=3)
        message = "Graph built successfully!Edges created"
    return render(request, "generate_edges.html", {"message": message})



def find_route(request):
    result = None
    if request.method == "POST":
        start_pin = request.POST.get("start")
        end_pin = request.POST.get("end")

        start_loc = Location.objects.filter(pincode = start_pin).first()

        end_loc = Location.objects.filter(pincode = end_pin).first()

        if not start_loc or not end_loc:
            result = {"error":"One or both pincodes not found in database."}
        else:
            result = a_star(start_loc, end_loc)
    
    return render(request, "find_route.html", {"result":result})
