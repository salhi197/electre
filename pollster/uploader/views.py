from django.shortcuts import render
from uploader.models import UploadForm,Upload
from django.http import HttpResponseRedirect
from django.urls import reverse
from pandas import DataFrame, read_csv
import random
from numpy import random

from django.http import JsonResponse
import pandas as pd
from re import search


# Create your views here.
def home(request):
    if request.method=="POST":
        img = UploadForm(request.POST, request.FILES)       
        if img.is_valid():
            img.save()  
            return HttpResponseRedirect(reverse('imageupload'))
    else:
        img=UploadForm()
    files=Upload.objects.all().order_by('-upload_date')
    return render(request,'home.html',{'form':img,'files':files})


def showFile(request, id): 
    file=Upload.objects.get(pk=id)
    #try to dispaly file in html table
    df = pd.read_excel(file.pic.file)
    data=   df.to_json(orient='split')
    return render(request,'acp.html',{'file':file,'data':data})


def Concordance(a, bh,Criteres,Poids,Performances,Seuils):
    conc = 0.0
    concs = 0.0
    poids = 0.0
    for critere in Criteres:
        poids += Poids[critere]
        ga = Performances[a][critere]
        gbh, qbh, pbh, vbh = Seuils[bh][critere]
        if gbh - ga >= pbh:
            conc = 0.0
        elif gbh - ga <= qbh:
            conc = 1.0
        elif qbh <= gbh - ga < pbh:
            conc = ((pbh + ga - gbh) / (pbh - qbh))
        concs += Poids[critere] * conc
    Cglob = concs / poids
    return Cglob

def Concordance2(bh, a,Criteres,Poids,Performances,Seuils):
    conc = 0.0
    concs = 0.0
    poids = 0.0
    for critere in Criteres:
        poids += Poids[critere]
        ga = Performances[a][critere]
        gbh, qbh, pbh, vbh = Seuils[bh][critere]
        if ga - gbh >= pbh:
            conc = 0.0
        elif ga - gbh < qbh:
            conc = 1.0
        elif qbh <= ga - gbh < pbh:
            conc = ((pbh - ga + gbh) / (pbh - qbh))
        concs += Poids[critere] * conc
    Cglob = concs / poids
    return Cglob


def DiscordanceCritere(a, bh, critere,Performances,Seuils):
    ga = Performances[a][critere]
    gbh, qbh, pbh, vbh = Seuils[bh][critere]
    discord = 0.0
    if gbh - ga < pbh:
        discord = 0.0
    elif gbh - ga >= vbh:
        discord = 1.0
    elif pbh <= gbh - ga < vbh:
        discord = ((-pbh - ga + gbh) / (vbh - pbh))
    return discord


def DiscordanceCritere2(bh, a, critere,Performances,Seuils):
    ga = Performances[a][critere]
    gbh, qbh, pbh, vbh = Seuils[bh][critere]
    discord = 0.0
    if ga - gbh < pbh:
        discord = 0.0
    elif ga - gbh >= vbh:
        discord = 1.0
    elif pbh <= ga - gbh < vbh:
        discord = ((-pbh - gbh + ga) / (vbh - pbh))
    return discord


def crédibilité(a, bh,Criteres,Performances,Seuils,Poids):
    mult = 1
    i = 0
    conc = Concordance(a, bh,Criteres,Poids,Performances,Seuils)
    for critere in Criteres:
        dicord = DiscordanceCritere(a, bh, critere,Performances,Seuils)
        if dicord > conc:
            i += 1
            mult = mult * ((1 - dicord) / (1 - conc))
    if i == len(Criteres):
        sigma_abh = conc * mult
    else:
        sigma_abh = conc
    return sigma_abh


def crédibilité2(bh, a,Criteres,Performances,Seuils,Poids):
    mult = 1
    i = 0
    conc = Concordance2(bh, a,Criteres,Poids,Performances,Seuils)
    for critere in Criteres:
        dicord = DiscordanceCritere2(bh, a, critere,Performances,Seuils)
        if dicord > conc:
            i += 1
            mult = mult * ((1 - dicord) / (1 - conc))
    if i == len(Criteres):
        sigma_abh = conc * mult
    else:
        sigma_abh = conc
    return sigma_abh


def electretri(wilaya,Classes,Criteres,Performances,Seuils,Poids,Lambda):
    PE = []
    PD = []
    PC = []
    PB = []
    PA = []
    OE = []
    OD = []
    OC = []
    OB = []
    OA = []
    for a in wilaya:
        z = 0
        l = 0
        # ['A', 'B', 'C', 'd', 'E']
        for classe in Classes[:-1]:
            l = l + 1
            if crédibilité(a[0], classe, Criteres, Performances, Seuils, Poids) >= Lambda and crédibilité2(classe, a[0],Criteres,Performances,Seuils,Poids) < Lambda:
                if classe == 'E' and z == 0:
                    OE.append(a)
                    z = z + 1
                    l = l + 1
                if classe == 'D' and z == 0:
                    OD.append(a)
                    z = z + 1
                    l = l + 1
                if classe == 'C' and z == 0:
                    OC.append(a)
                    z = z + 1
                    l = l + 1
                if classe == 'B' and z == 0:
                    OB.append(a)
                    z = z + 1
                    l = l + 1
        print('this is oooooooooooptttttti',l)
        if l == 4:
            OA.append(a)

    for a in wilaya:
        i = 0
        l = 0
        # ['A', 'B', 'C', 'd', 'E']

        for classe in Classes[:-1]:
            l = l + 1
            if crédibilité(a[0], classe, Criteres, Performances, Seuils, Poids) < Lambda and crédibilité2(classe, a[0],Criteres,Performances,Seuils,Poids) >= Lambda:
                if classe == 'E' and i == 0:
                    PD.append(a)
                    i = i + 1
                    l = l + 1
                if classe == 'D' and i == 0:
                    PC.append(a)
                    i = i + 1
                    l = l + 1
                if classe == 'C' and i == 0:
                    PB.append(a)
                    i = i + 1
                    l = l + 1
                if classe == 'B' and i == 0:
                    PA.append(a)
                    i = i + 1
                    l = l + 1
        print('this is pppppppppppppppppppppesssssssssi', l)
        if l == 4:
            PA.append(a)
    resulta = [OE, OD, OC, OB, OA,PE, PD, PC, PB, PA]
    return resulta
    

def launchElectre(request,id):
    file=Upload.objects.get(pk=id)
    df = pd.read_excel(file.pic.file)
    Classes = ['E', 'D', 'C', 'B', 'A']


    lenclasses = len(Classes)
    minus = lenclasses+3
    dimensions = df.shape
    nombrepdv=dimensions[0]-minus
    Poids=(df.iloc[-1]).to_dict()
    Poids.pop('Alternatives')

    Criteres = list(Poids.keys())
    Criteres.pop()

    first_column = (df.iloc[:, 0]).to_dict()
    values = first_column.values()
    values_list = list(values)
    Actions = []
    for i in range(0,dimensions[0]-minus):
        Actions.append(values_list[i])

    # pdv with wilaya
    col_wilaya = (df.iloc[:dimensions[0] - minus, dimensions[1] - 1:dimensions[1]]).to_dict('list')
    pdv_wilaya = list(col_wilaya.values())
    pdvwi = pdv_wilaya[0].copy()
    zip_object = zip(Actions, pdvwi)
    wilaya = []
    for element1, element2 in zip_object:
        wilaya.append((element1, element2))

    per = (df.iloc[:dimensions[0]-minus, 1:dimensions[1]-1]).to_dict('records')

    Performances = {}
    for i in range(0,len(Actions)):
        Performances[Actions[i]] = per[i]

    seu = (df.iloc[dimensions[0]-minus:dimensions[0]-1, 1:]).to_dict('split')
    p = lenclasses - 1
    q = lenclasses
    v = lenclasses + 1
    Seuils = {}
    for n in range(0,minus-4):
        t = {}
        for m in range(0,minus-3):
            t[seu['columns'][m]] = [seu['data'][n][m],seu['data'][p][m],seu['data'][q][m],seu['data'][v][m]]
        Seuils[Classes[n]] = t

    Lambda = 0.75

    resulta = electretri(wilaya,Classes,Criteres,Performances,Seuils,Poids,Lambda)

    return render(request,'electre.html',
        {
            "resulta":resulta,
            "resulta0":resulta[0],"len0":len(resulta[0]),
            "resulta1":resulta[1],"len1":len(resulta[1]),
            "resulta2":resulta[2],"len2":len(resulta[2]),
            "resulta3":resulta[3],"len3":len(resulta[3]),
            "resulta4":resulta[4],"len4":len(resulta[4]),
            "resulta5":resulta[5],"len5":len(resulta[5]),
            "resulta6":resulta[6],"len6":len(resulta[6]),
            "resulta7":resulta[7],"len7":len(resulta[7]),
            "resulta8":resulta[8],"len8":len(resulta[8]),
            "resulta9":resulta[9],"len9":len(resulta[9]),
            "nombre_pdv":nombrepdv
            
        })
    
