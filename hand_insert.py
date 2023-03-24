import logging

from toroplay import Toroplay

film_data = {
    "title": "The Blacklist - Saison 10",
    "description": "\nHistoire de la série The Blacklist - Saison 10 en streaming complet : Raymond « Red » Reddington, l’un des fugitifs les plus recherchés par le FBI, se rend en personne au quartier général du FBI à Washington. Il affirme avoir les mêmes intérêts que le FBI : faire tomber des criminels dangereux et des terroristes. Reddington coopérera, mais insiste pour ne parler qu’à Elizabeth Keen, une profileuse inexpérimentée du FBI. Keen s’interroge sur l’intérêt soudain que Reddington lui porte, bien qu’il soutienne que Keen est très spéciale. Après que le FBI a fait tomber un terroriste sur lequel il a fourni des informations, Reddington révèle que ce terroriste n’est que le premier de beaucoup d’autres à venir : durant les deux dernières décennies, il a fait une liste des criminels et terroristes qu'il croit introuvable par le FBI parce que ce dernier ignorait leur existence et que ce sont les plus importants. Reddington l’appelle « La Liste noire » (« The Blacklist »).\n",
    "post_type": "series",
    "trailer_id": "",
    "fondo_player": "https://i.imgur.com/Ww2RUNT.jpg",
    "poster_url": "https://i.imgur.com/Ww2RUNT.jpg",
    "extra_info": {
        "Titre Original": "The Blacklist / 2023",
        "Genre": "Drame, Crime, Mystère",
        "Réalisé par": "Jon Bokenkamp",
        "Avec": "James Spader, Diego Klattenhoff, Harry Lennix, Hisham Tawfiq, Anya Banerjee",
    },
}

film_links = {
    "The Blacklist - Saison 10 épisode 1 en VF": {},
    "The Blacklist - Saison 10 épisode 2 en VF": {},
    "The Blacklist - Saison 10 épisode 3 en VF": {},
    "The Blacklist - Saison 10 épisode 4 en VF": {},
    "The Blacklist - Saison 10 épisode 1 EN VOSTFR": {
        "ViDO": "https://vido.lol/embed-k7bevehqmod2.html",
        "UQLOAD": "https://uqload.co/embed-fneas1sxer5h.html",
        "NETU": "https://younetu.com/e/oLmIRLpNqOtx",
        "EVOLOAD": "https://flixeo.xyz/tokyo/newPlayer.php?id=62611d41-ae57-4fac-9135-770779e59859",
        "UPTOSTREAM": "https://opsktp.com/uptoboxx15/newPlayer.php?id=79728f7f-5ae4-4369-a0ff-73526a1d07bf",
    },
    "The Blacklist - Saison 10 épisode 2 EN VOSTFR": {
        "ViDO": "https://vido.lol/embed-mnczqic5jyzd.html",
        "UQLOAD": "https://uqload.co/embed-9xqjjk0e7uf4.html",
        "NETU": "https://younetu.com/e/oJRJim95TRlz",
        "EVOLOAD": "https://flixeo.xyz/tokyo/newPlayer.php?id=fd96bc89-4197-43a6-abeb-fdc0681c9038",
        "UPTOSTREAM": "https://opsktp.com/uptoboxx15/newPlayer.php?id=247fb501-3338-4831-bc81-e8db400cb7cd",
    },
    "The Blacklist - Saison 10 épisode 3 EN VOSTFR": {
        "ViDO": "https://vido.lol/embed-p8njme7o7v60.html",
        "UQLOAD": "https://uqload.co/embed-xb3r3d0ga1st.html",
        "NETU": "https://younetu.com/e/JJr933FcJaIm",
        "EVOLOAD": "https://flixeo.xyz/tokyo/newPlayer.php?id=5dcbbf67-4540-48a3-865a-1164a52797d2",
        "UPTOSTREAM": "https://opsktp.com/uptoboxx15/newPlayer.php?id=7bd6a29a-2fb2-428f-aba2-ad512b161c82",
    },
    "The Blacklist - Saison 10 épisode 4 EN VOSTFR": {
        "ViDO": "https://vido.lol/embed-bks0m7h6cijg.html",
        "UQLOAD": "https://uqload.co/embed-4v0axn45y52d.html",
        "NETU": "https://younetu.com/e/PRLk5IUEgkzR",
        "EVOLOAD": "https://flixeo.xyz/tokyo/newPlayer.php?id=1ea427b1-2752-44b5-b3ba-0279240e6394",
        "UPTOSTREAM": "https://opsktp.com/uptoboxx15/newPlayer.php?id=f67400cd-490b-46b9-895b-a408825e1b4c",
    },
    "The Blacklist - Saison 10 épisode 25 EN VOSTFR": {"Player 1": ""},
}

logging.basicConfig(format="%(asctime)s %(levelname)s:%(message)s", level=logging.INFO)


def main():
    Toroplay(film_data, film_links).insert_film()


if __name__ == "__main__":
    main()
