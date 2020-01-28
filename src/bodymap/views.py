from django.shortcuts import render
from random import randint
import json


from .forms import bodypartChoice, CASUpload
from .loadMapping import assaysMapping
from .mapChem import mapChem
from .prepInputChem import prepChem


# Create your views here.
def index(request):

    if not "name_session" in request.session.keys():
        a = randint(0, 1000000)
        request.session.get("name_session", a)
        request.session["name_session"] = a
    return render(request, 'bodymap/index.html', {
    })

def help(request):
    return render(request, 'bodymap/help.html', {
    })


def mappingChemicalToBody(request, typeChem=""):


    # form for bodypart
    if request.method == 'GET':
        formCAS = CASUpload()
        return render(request, 'bodymap/chemTobody.html', {"formCAS": formCAS, "Error": "0"})
    else:
        formCAS = CASUpload(request.POST)

    # run map with new chem
    if typeChem == "name":
        CAS = formCAS.clean_name()
    else:
        CAS = formCAS.clean_CAS()

    dchem = prepChem(CAS)
    if dchem == 1:
        return render(request, 'bodymap/ChemMapping.html', {"Error": "1"})

    cmapChem = mapChem(CAS)
    cmapChem.loadFromDB("bodymap_assay_mapping_new", "bodymap_assay_ac50", "bodymap_genemap")
    dmap = cmapChem.mapChemToBody()
    dmapJS = json.dumps(dmap)
    dchemJS = json.dumps(dchem)
    typeJS = json.dumps("chem")


    return render(request, 'bodymap/ChemMapping.html', {"dmap": dmapJS, "dchem": dchemJS, "Error": "0", "Type":"chem", "TypeJS":typeJS})
