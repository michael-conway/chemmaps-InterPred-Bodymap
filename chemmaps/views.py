from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render
from django.views.generic import TemplateView
from django.core.files.storage import default_storage
from random import randint
import json
from re import search


from .forms import UploadChemList, descDrugMapChoice, descDSSToxMapChoice, descDSSToxChoice, uploadList
from .content import uploadSMILES
from .toolbox import loadMatrixToDict
from .JSbuilder import JSbuilder
from .toolbox import createFolder
from .DSSToxPrep import DSSToxPrep

from os import path


def test(request, toto):

    return HttpResponse('Slug parameter is: ' + toto)



def index(request):

    if not "name_session" in request.session.keys():
        a = randint(0, 1000000)
        request.session.get("name_session", a)
        request.session["name_session"] = a
    return render(request, 'chemmaps/index.html')



def launchHelp(request):
    return render(request, 'chemmaps/help.html', {
    })



def download(request, name):

    name_session = request.session.get("name_session")
    prsession = path.abspath("./temp") + "/" + str(name_session) + "/"

    file_path = prsession + name + ".csv"
    if path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + path.basename(file_path)
            return response
    raise Http404




def launchMap(request, map):

    name_session = request.session.get("name_session")

    # open file with
    prsession = path.abspath("./temp") + "/" + str(name_session) + "/"

    if request.method == 'GET':
        form_smiles = UploadChemList()
        if map == "DrugMap":
            formDesc = descDrugMapChoice()
        elif map == "PFASMap" or map == "Tox21Map":
            formDesc = descDSSToxChoice()
        else:
            formDesc = descDSSToxMapChoice()
        formUpload = uploadList()
    else:
        form_smiles = UploadChemList(request.POST)
        if map == "DrugMap":
            formDesc = descDrugMapChoice(request.POST)
        elif map == "PFASMap" or map == "Tox21Map":
            formDesc = descDSSToxChoice(request.POST)
        else:
            formDesc = descDSSToxMapChoice(request.POST)
        formUpload = uploadList(request.POST, request.FILES)


    # If data is valid, proceeds to create a new post and redirect the user
    if form_smiles.is_valid() == True:

        content = form_smiles.cleaned_data["content"]
        content = content.replace("\r", "")
        content = content.split("\n")
        content = list(dict.fromkeys(content))
        if len(content) > 200:
            return render(request, 'chemmaps/launchMap.html', {"form_info":formDesc, "form_smiles":form_smiles,
                                                           "from_upload": formUpload, "ErrorLine": "1", "map":map})

        prsession = path.abspath("./temp") + "/" + str(name_session) + "/"
        createFolder(prsession, 1)

        cinput = uploadSMILES(content, prsession)
        cinput.prepListSMILES()

        return render(request, 'chemmaps/smilesprocess.html', {"dSMILESIN": cinput.dclean["IN"], "ERRORSmiles": str(cinput.err),
                                                            "dSMILESOUT": cinput.dclean["OUT"], "map":map})


    elif formUpload.is_valid() == True:

        prsession = path.abspath("./temp") + "/" + str(name_session) + "/"
        createFolder(prsession, 1)

        pfileserver = prsession + "upload.txt"
        with open(pfileserver, 'wb+') as destination:
            for chunk in formUpload.files["docfile"].chunks():
                destination.write(chunk)
        destination.close()

        filin = open(pfileserver, "r")
        try:
            content = filin.read()
            filin.close()

            lsmiles = content.split("\n")
            lsmiles = list(dict.fromkeys(lsmiles))
            if len(lsmiles) > 100:
                return render(request, 'chemmaps/launchMap.html', {"form_info": formDesc, "form_smiles": form_smiles,
                                                                   "from_upload": formUpload, "ErrorFile": "1",
                                                                   "map": map})
            cinput = uploadSMILES(lsmiles, prsession)
            cinput.prepListSMILES()

            return render(request, 'chemmaps/smilesprocess.html', {"dSMILESIN": cinput.dclean["IN"],
                                                                   "ERRORSmiles": str(cinput.err),
                                                                   "dSMILESOUT": cinput.dclean["OUT"], "map": map})

        except:
            filin.close()
            return render(request, 'chemmaps/launchMap.html', {"form_info": formDesc, "form_smiles": form_smiles,
                                                               "from_upload": formUpload, "ErrorFile": "1", "map": map})


    elif formDesc.is_valid() == True:

        ldescMap = formDesc.clean_desc()
        if ldescMap == "ERROR":
            return render(request, 'chemmaps/launchMap.html', {"form_info":formDesc, "form_smiles":form_smiles,
                                                           "from_upload": formUpload, "Error": "1", "map":map})

        if map == "DSSToxMap":

            chemIn = formDesc.cleaned_data['chem']
            build = DSSToxPrep(chemIn, ldescMap, prsession)
            if not search("DTXSID", chemIn):
                build.err = 1
            else:
                build.loadChemMapCenterChem(chemIn, center = 1, nbChem = 10000)
            if build.err == 1:
                return render(request, 'chemmaps/launchMap.html', {"form_info": formDesc, "form_smiles": form_smiles,
                                                                   "from_upload": formUpload, "Error": "0", "map": map,
                                                                   "ErrorDSSTox":"1"})
            dcoord = json.dumps(build.coord)
            dinfo = json.dumps(build.dinfo)
            dneighbor = json.dumps(build.dneighbor)
            dSMILESClass = json.dumps(build.dSMILES)
            ldescJS = list(build.dinfo[list(build.dinfo.keys())[0]].keys())


        else:
            build = JSbuilder(map, list(ldescMap))
            build.loadMap()

            dJS = build.generateJS()
            #   format for JS
            dcoord = json.dumps(dJS["coord"])
            dinfo = json.dumps(dJS["info"])
            dneighbor = json.dumps(dJS["neighbor"])
            dSMILESClass = json.dumps(dJS["SMILESClass"])
            ldescJS = list(dJS["info"][list(dJS["info"].keys())[0]].keys())

        mapJS = json.dumps(map)
        prSessionJS = json.dumps(prsession[1:])

        return render(request, 'chemmaps/Map3D.html', {"dcoord": dcoord, "dinfo": dinfo, "dneighbor": dneighbor,
                                                             "dSMILESClass":dSMILESClass,
                                                             "ldesc":ldescJS, "map":map, "mapJS": mapJS,"prSessionJS":prSessionJS })

    else:
        return render(request, 'chemmaps/launchMap.html', {"form_info":formDesc, "form_smiles":form_smiles,
                                                           "from_upload": formUpload, "Error": "0", "map":map})


# case of automatic launch -> Comptox
def launchDSSToxMap(request, DTXSID):

    # fault Ldesc
    ldescMap = ["LD50_mgkg", "CATMoS_VT_pred", "EPA_category", "MolWeight","LogP_pred"]

    build = DSSToxPrep(DTXSID, ldescMap, "")
    build.loadChemMapCenterChem(DTXSID, center = 1, nbChem = 10000)
    if build.err == 1:
        return render(request, 'chemmaps/index.html', {"DTXSID":DTXSID})

    else:
        dcoord = json.dumps(build.coord)
        dinfo = json.dumps(build.dinfo)
        dneighbor = json.dumps(build.dneighbor)
        dSMILESClass = json.dumps(build.dSMILES)
        ldescJS = list(build.dinfo[list(build.dinfo.keys())[0]].keys())

        mapJS = json.dumps("DSSToxMap")
        prSessionJS = json.dumps("")

        return render(request, 'chemmaps/Map3D.html', {"dcoord": dcoord, "dinfo": dinfo, "dneighbor": dneighbor,
                                                             "dSMILESClass":dSMILESClass,
                                                             "ldesc":ldescJS, "map":"DSSToxMap", "mapJS": mapJS,"prSessionJS":prSessionJS })



def computeDescriptor(request, map):


    name_session = request.session.get("name_session")
    #print(name_session)

    # open file with
    prsession = path.abspath("./temp") + "/" + str(name_session) + "/"
    
    dSMI = loadMatrixToDict(prsession + "smiClean.csv", sep="\t")

    cinput = uploadSMILES(dSMI, prsession)
    lfileDesc = cinput.computeDesc(map)

    if cinput.err == 1:
        return render(request, 'chemmaps/descriptor.html', {"map": map, "dSMILESIN": cinput.dclean["IN"],
                                                            "ddesc":{}, "dSMILESOUT": cinput.dclean["OUT"],
                                                            "ErrorDesc": "1"})

    # form for descriptors
    if request.method == 'GET':
        if map == "DrugMap":
            formDesc = descDrugMapChoice()
        elif map == "PFASMap" or map == "Tox21Map":
            formDesc = descDSSToxChoice()
        else:
            formDesc = descDSSToxMapChoice()
    else:
        if map == "DrugMap":
            formDesc = descDrugMapChoice(request.POST)
        else:
            formDesc = descDSSToxChoice(request.POST)

    # run map with new chem
    if formDesc.is_valid() == True:
        ldescMap = formDesc.clean_desc()
        if ldescMap == "ERROR":
            return render(request, 'chemmaps/descriptor.html',{"map": map, "dSMILESIN":cinput.dclean["IN"],
                                                            "dSMILESOUT": cinput.dclean["OUT"], "ddesc":cinput.ddesc,
                                                            "form_info": formDesc, "Error": "1"})
        else:
            if map == "DSSToxMap":

                build = JSbuilder(map, ldescMap, prsession)
                build.generateCoords(lfileDesc[0], lfileDesc[1])
                build.findinfoTable()
                build.findneighbor()

                cDSSTox = DSSToxPrep(build.dchemAdd, ldescMap, prsession)
                cDSSTox.loadChemMapAddMap()

                dcoord = json.dumps(cDSSTox.coord)
                dinfo = json.dumps(cDSSTox.dinfo)
                dneighbor = json.dumps(cDSSTox.dneighbor)
                dSMILESClass = json.dumps(cDSSTox.dSMILES)

                ldesc = list(cDSSTox.dinfo[list(cDSSTox.dinfo.keys())[0]].keys())


            else:

                build = JSbuilder(map, ldescMap, prsession)
                build.loadMap()
                # manage new chemical for the JS
                build.generateCoords(lfileDesc[0], lfileDesc[1])# from computed descriptors
                build.findinfoTable()
                build.findneighbor()

                dJS = build.generateJS()
                #   format for JS
                dcoord = json.dumps(dJS["coord"])
                dinfo = json.dumps(dJS["info"])
                dneighbor = json.dumps(dJS["neighbor"])
                dSMILESClass = json.dumps(dJS["SMILESClass"])
                ldesc = list(dJS["info"][list(dJS["info"].keys())[0]].keys())
            #a = cDSSTox.dinfo
            #b = cDSSTox.dinfo["1"]
            #dddd

            prSessionJS = json.dumps(prsession[1:])
            mapJS = json.dumps(map)


        return render(request, 'chemmaps/Map3D.html', {"dcoord": dcoord, "dinfo": dinfo, "dneighbor": dneighbor,
                                                           "dSMILESClass": dSMILESClass, "ldesc": ldesc,
                                                            "map": map, "mapJS": mapJS, "prSessionJS":prSessionJS})

    else:
        return render(request, 'chemmaps/descriptor.html', {"map": map, "dSMILESIN":cinput.dclean["IN"],
                                                            "dSMILESOUT": cinput.dclean["OUT"], "ddesc":cinput.ddesc,
                                                            "form_info": formDesc, "Error": "0"})








