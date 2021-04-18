import sqlite3
from tkinter import *
from functools import*
from tkinter.ttk import *

def creer_connexion(fichier='datafilms.db'):
    '''fonction qui établit une connexion avec une base de données. Prends en argument une chaîne de caractère contenant le nom du fichier. Retourne l'objet effectuant la connexion'''
    connexion=sqlite3.connect(fichier)
    return connexion

def requ_real(entry):
    '''lance une requete pour trouver les films d'un réalisateur. Prends en entrée une connexion à une base de données et une chaîne de caractères. Retourne le résultat de la requête'''
    return requete(entry,'realisateur')

def requ_acteur(entry):
    '''lance une requete pour une liste de film contenant l'acteur. Prends en entrée une connexion à une base de donnée et une chaîne de caractère et retourne la liste de fims'''
    return requete(entry,'acteur')

def requ_film(entry):
    '''lance une requete pour un film. Prends en entrée une connexions à une base de données et une chaîne de caractère. Retourne le résultat de la requête'''
    return requete(entry,'titre')

def requete(entry,genre):
    '''fonction qui prend en paramètre une connexion à une base de données, 2 chaînes de caractères. Retourne une liste des résultats obtenus dans la base de données'''

    #######
    #def get_most_popular_actor(liste):
    '''fonction qui fait le total des recettes pour chaque acteur et garde le premier. Prends en argument la liste d'id de films #retournée par SQLite.
    Malheuresement, les acteurs sont souvent des figurants donc ils ont des recettes importantes mais sont inconnus. Je n'ai donc pas gardé cette fonction,je la trouvais non pertinente. Malgré les heures de travail'''
    #    acteur=[[] for i in range(len(liste))]
    #    for i in range(len(liste)):
    #        request='SELECT A.acteur FROM LesFilms F JOIN LesActeurs A #ON (F.film_id=A.film_id) WHERE F.film_id="'+str(liste[i][0]#)+'"'
    #        curseur=db.cursor()
    #        curseur.execute(request)
    #        l=curseur.fetchall()
    #        for b in range(len(l)):
    #            acteur[i].append([l[b][0]])
    #    for i in range(len(acteur)):
    #        for b in range(len(acteur[i])):
    #            request='SELECT SUM(F.recette)FROM LesFilms F JOIN #LesActeurs A ON (F.film_id=A.film_id) WHERE acteur="'#+str(acteur[i][b][0])+'"'
    #            curseur=db.cursor()
    #            curseur.execute(request)
    #            l=curseur.fetchall()
    #            acteur[i][b].append(l[0][0])
    #    acteur=sorted(acteur,key=lambda acteur:acteur[1],reverse=True)
    #    for i in range(len(acteur)):
    #        acteur[i]=acteur[i][:4]
    #    print(acteur)
    #####


    db=creer_connexion()#crée la connexion
    voyelle='aeiouy'#pour anticiper les erreurs de l'utilisateur
    request='SELECT DISTINCT(F.film_id) FROM LesFilms F JOIN LesRealisateurs R JOIN LesActeurs A ON (F.film_id=R.film_id and A.film_id=F.film_id and A.film_id=R.film_id) WHERE '+genre+'="'+entry+'"' #crée le début de la requête qui va récuperer les idendifiants distincts de film où le genre (réalisateur,film,acteur) équivaut à celui rentré par l'utilisateur
    request=request+' or '+genre+' like "%'+entry+'%"' #rajoute à la requete une condition où l'entrée de l'utilisateur est juste une partie de la 'réponse'. Permet de trouver Quentin Tarantino en tapant juste 'Tarantino'

    for i in range(len(entry)): #pour chaque lettre de l'entrée
        replace=[]
        if entry[i] in voyelle: #si la lettre est une voyelle
            replace.append(entry[0:i]+'%'+entry[i+1:]) #crée une chaîne de caractère où la lettre est remplacée par un %
            replace.append('%'+entry[0:i]+'%'+entry[i+1:]+'%')#crée une chaîne de caractère qui contient l'entrée avec des pourcentages au début, à la fin, et à l'index
            for element in replace:
                request=request+' or '+genre+' like "'+element+'"' #rajoute à la rêquete actuelle un or avec la nouvelle chaine de caractère (permet d'anticiper les erreurs)

    request=request+';'#termine la requête avec un point virgule
    
    curseur=db.cursor()
    curseur.execute(request)#execute la commande
    resultats=curseur.fetchall()#récupère les id de films.
    index=[]
    for i in range(0,len(resultats)):
        demande='SELECT F.film_id, F.titre, F.anSortie,F.duree, F.vo, F.genres, F.recette, R.realisateur FROM LesRealisateurs R JOIN LesFilms F ON (R.film_id=F.film_id) WHERE F.film_id="'+str(resultats[i][0])+'"'#récupère les infos du film pour chaque id obtenu précédemment
        #execute cette demande et récupère les résultats
        curseur=db.cursor()
        curseur.execute(demande)
        l=curseur.fetchall()

        for i in range(len(l)):
            element=[]
            for b in range(len(l[i])):
                element.append(l[i][b])#crée une liste non plus imbriquée dans un tuple
            index.append(element)#l'ajoute à la liste de tout les films

    index=sorted(index, key=lambda index:index[6],reverse=True)#tri les films par recette descendante

    db.close()#ferme l'accès à la base de données
    return index #retourne la liste des films


def result():
    '''fonction qui affiche le résultat,un bouton pour quitter et un bouton pour recommencer'''
    display=Frame(fenetre,borderwidth=2, relief=GROOVE)

    genre=int(typedata.get())
    if genre==1:
        resultat=requ_film(entry.get())
    if genre==2:
        resultat=requ_real(entry.get())
    if genre==3:
        resultat=requ_acteur(entry.get())

    tableau= Treeview(display,height=20)#crée un tableau
    columns=('Nom','Année','Durée','Langue','Genres','Recette','Réalisateur')
    tableau['columns']=columns #crée des colonnes avec la liste précédente

    def Acteur(a):
        '''fonction qui affiche une fenetre pop-up avec la liste des acteurs du film.'''
        curItem = tableau.focus() 
        dictionnaire=tableau.item(curItem) #récupère l'id du film où l'utilisateur a cliqué
        if type(dictionnaire['values'])==list:
            titrefilm=dictionnaire['values'][0]
            db=creer_connexion()

            demande='SELECT acteur FROM LesActeurs A JOIN LesFilms F ON (A.film_id=F.film_id) WHERE F.titre="'+str(titrefilm)+'"'#récupère les infos du film pour chaque id obtenu précédemment
            #execute cette demande et récupère les résultats
            curseur=db.cursor()
            curseur.execute(demande)
            l=curseur.fetchall()

            pop=Toplevel(fenetre) #crée un pop up
            pop.geometry("400x300")
            texte=Label(pop,text='Voici la liste des acteurs! Scroll pour la voir en entier')
            pop.title("Acteurs du film "+titrefilm)
            tableauActeur= Treeview(pop,height=250)#crée un tableau
            tableauActeur['columns']='Nom'
            tableauActeur.heading('Nom',text="Nom des acteurs")
            tableauActeur['show'] = 'headings'#montre les noms
            for i in range(len(l)):
                tableauActeur.insert('','end',iid=l[i][0],values=l[i])#ajoute chaque résultat au tableau. Garde le nom de l'acteur comme identifiant unique
            tableauActeur.pack(pady=20,padx=10)





    def treeview_sort_column(treeview: tableau, col, reverse: bool):
        """
        tri le tableau par la colonne sur laquelle on clique
        """
        try:
            data_list = [
                (int(treeview.set(k, col)), k) for k in treeview.get_children("")
            ]
        except Exception:
            data_list = [(treeview.set(k, col), k) for k in treeview.get_children("")]

        data_list.sort(reverse=reverse)

        # met les items dans la position triée
        for index, (val, k) in enumerate(data_list):
            treeview.move(k, "", index)

        # change l'ordre de tri la prochaine fois qu'on clique
        treeview.heading(
            column=col,
            text=col,
            command=lambda _col=col: treeview_sort_column(
                treeview, _col, not reverse
            ),
        )
    #permet à chaque colonne d'être triée lorsque l'on clique dessus
    tableau.bind('<ButtonRelease-1>', Acteur)
    for col in columns:
        tableau.heading(col, text=col, command=lambda _col=col: \
            treeview_sort_column(tableau, _col, False))

    #crée un titre pour chaque colonne
    tableau.heading('Nom',text='Nom du film')
    tableau.heading('Année',text='Année de sortie')
    tableau.heading('Durée',text='Durée en minutes')
    tableau.heading('Langue',text='Langue de la VO')
    tableau.heading('Genres',text='Genres')
    tableau.heading('Recette',text='Recette du film')
    tableau.heading('Réalisateur',text='Réalisateur')
    tableau['show'] = 'headings'#montre les noms
    

    display.grid(row=7,column=0)
    tableau.grid(row=8,column=0)
    warning=Label(display,text="Scroll pour voir les résultats!\nPour voir la liste des acteurs d'un film, clique dessus! (il faudra scroller aussi) \nSi une donnée n'existe pas ou est nulle, c'est qu'elle est manquante à la base de données",font=("Helvetica",13),justify=CENTER)
    warning.grid(row=7,column=0)
    for element in resultat:
        tableau.insert('','end',iid=element[0],values=(element[1],element[2],element[3],element[4],element[5],element[6],element[7]))#ajoute chaque résultat au tableau. Garde le film_id comme identifiant unique


fenetre=Tk()
fenetre.title('Allociné')

recherche=Frame(fenetre,borderwidth=2, relief=GROOVE)
pres=Label(recherche, text="Bienvenue, rentre le nom d'un acteur, d'un film ou d'un réalisateur, le logiciel s'occupe du reste!")
#boutons nécessaires au lancement de la recherche
global entry
entry=StringVar()
entry.set('Tarantino')
entree=Entry(recherche,textvariable=entry,width=20)
enter=Button(recherche,text='Lancer la recherche',command=result)
quitter=Button(recherche,text='Quitter le logiciel',command=fenetre.quit)
#création de boutons pour choisir le type de données
global typedata
typedata=StringVar(recherche,2)
titre=Radiobutton(recherche,text='Film',variable=typedata, value=1).grid(row=3)
realisateur=Radiobutton(recherche,text='Réalisateur',variable=typedata,value=2).grid(row=4)
acteur=Radiobutton(recherche,text='Acteur',variable=typedata,value=3).grid(row=5)

#met en place chaque élément
recherche.grid(row=0,column=0)
pres.grid(row=1,column=0)
entree.grid(row=2,column=0)
enter.grid(row=6,column=0)
quitter.grid(row=6,column=1)
mainloop()