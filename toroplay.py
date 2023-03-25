import base64
import logging
import re
from datetime import datetime, timedelta
from html import escape
from pathlib import Path
from time import sleep

from phpserialize import serialize
from slugify import slugify

from _db import database
from settings import CONFIG

logging.basicConfig(format="%(asctime)s %(levelname)s:%(message)s", level=logging.INFO)


class ToroplayHelper:
    def generate_trglinks(
        self,
        server: str,
        link: str,
        lang: str = "English",
        quality: str = "HD",
    ) -> str:
        if "http" not in link:
            link = "https:" + link

        server_term_id, isNewServer = self.insert_terms(
            post_id=0, terms=server, taxonomy="server"
        )

        lang_term_id, isNewLang = self.insert_terms(
            post_id=0, terms=lang, taxonomy="language"
        )

        quality_term_id, isNewQuality = self.insert_terms(
            post_id=0, terms=quality, taxonomy="quality"
        )

        link_data = {
            "type": "1",
            "server": str(server_term_id),
            "lang": int(lang_term_id),
            "quality": int(quality_term_id),
            "link": base64.b64encode(bytes(escape(link), "utf-8")).decode("utf-8"),
            "date": self.get_timeupdate().strftime("%d/%m/%Y"),
        }
        link_data_serialized = serialize(link_data).decode("utf-8")

        return f's:{len(link_data_serialized)}:"{link_data_serialized}";'

    def format_text(self, text: str) -> str:
        return text.strip("\n").replace('"', "'").strip()

    def error_log(self, msg: str, log_file: str = "failed.log"):
        datetime_msg = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        Path("log").mkdir(parents=True, exist_ok=True)
        with open(f"log/{log_file}", "a") as f:
            print(f"{datetime_msg} LOG:  {msg}\n{'-' * 80}", file=f)

    def get_season_number(self, strSeason: str) -> int:
        strSeason = strSeason.split(" ")[0]
        res = ""
        for ch in strSeason:
            if ch.isdigit():
                res += ch

        return res

    def get_episode_title_and_language_and_number(self, episode_title: str) -> str:
        title = episode_title.lower()

        if title.endswith("en vf"):
            language = "VF"
            title = title.replace("en vf", "").strip()

        elif title.endswith("en vostfr"):
            language = "VOSTFR"
            title = title.replace("en vostfr", "").strip()
        else:
            language = "VO"

        pattern = r"épisode\s(\d+(\.\d+)?)"
        match = re.search(pattern, title)
        if match:
            number = match.group(1)
        else:
            self.error_log(
                msg=f"Unknown episode number for: {title}",
                log_file="toroplay_get_episode_title_and_language_and_number.log",
            )
            number = ""

        title = title.title()

        return [title, language, number]

    def get_title_and_season_number(self, title: str) -> list:
        title = title
        season_number = "1"

        try:
            for seasonSplitText in CONFIG.SEASON_SPLIT_TEXTS:
                if seasonSplitText in title:
                    title, season_number = title.split(seasonSplitText)
                    break

        except Exception as e:
            self.error_log(
                msg=f"Failed to find title and season number\n{title}\n{e}",
                log_file="toroplay.get_title_and_season_number.log",
            )

        return [
            self.format_text(title),
            self.get_season_number(self.format_text(season_number)),
        ]

    def insert_postmeta(self, postmeta_data: list, table: str = "postmeta"):
        database.insert_into(
            table=f"{CONFIG.TABLE_PREFIX}{table}", data=postmeta_data, is_bulk=True
        )

    def generate_film_data(
        self,
        title,
        description,
        post_type,
        trailer_id,
        fondo_player,
        poster_url,
        extra_info,
    ):
        post_data = {
            "description": description,
            "title": title,
            "post_type": post_type,
            # "id": "202302",
            "youtube_id": f"{trailer_id}",
            # "serie_vote_average": extra_info["IMDb"],
            # "episode_run_time": extra_info["Duration"],
            "fondo_player": fondo_player,
            "poster_url": poster_url,
            # "category": extra_info["Genre"],
            # "stars": extra_info["Actor"],
            # "director": extra_info["Director"],
            # "release-year": [extra_info["Release"]],
            # "country": extra_info["Country"],
        }

        key_mapping = {
            "Réalisé par": "cast",
            "Avec": "cast",
            "Acteurs": "cast",
            "Genre": "category",
            "Date de sortie": "annee",
            "Réalisateur": "directors",
        }

        for info_key in key_mapping.keys():
            if info_key in extra_info.keys():
                post_data[key_mapping[info_key]] = extra_info[info_key]

        for info_key in ["cast", "directors"]:
            if info_key in post_data.keys():
                post_data[f"{info_key}_tv"] = post_data[info_key]

        return post_data

    def get_timeupdate(self) -> datetime:
        timeupdate = datetime.now() - timedelta(hours=7)

        return timeupdate

    def generate_post(self, post_data: dict) -> tuple:
        timeupdate = self.get_timeupdate()
        data = (
            0,
            timeupdate.strftime("%Y/%m/%d %H:%M:%S"),
            timeupdate.strftime("%Y/%m/%d %H:%M:%S"),
            post_data["description"],
            post_data["title"],
            "",
            "publish",
            "open",
            "open",
            "",
            slugify(post_data["title"]),
            "",
            "",
            timeupdate.strftime("%Y/%m/%d %H:%M:%S"),
            timeupdate.strftime("%Y/%m/%d %H:%M:%S"),
            "",
            0,
            "",
            0,
            post_data["post_type"],
            "",
            0,
        )
        return data

    def insert_post(self, post_data: dict) -> int:
        data = self.generate_post(post_data)
        post_id = database.insert_into(table=f"{CONFIG.TABLE_PREFIX}posts", data=data)
        return post_id

    def insert_film(self, post_data: dict) -> int:
        try:
            post_id = self.insert_post(post_data)
            timeupdate = self.get_timeupdate()

            postmeta_data = [
                (post_id, "_edit_last", "1"),
                (post_id, "_edit_lock", f"{int(timeupdate.timestamp())}:1"),
                # _thumbnail_id
                (post_id, "tr_post_type", "2"),
                (post_id, "field_title", post_data["title"]),
                # (
                #     post_id,
                #     "field_trailer",
                #     CONFIG.YOUTUBE_IFRAME.format(post_data["youtube_id"]),
                # ),
                (
                    post_id,
                    "poster_hotlink",
                    post_data["poster_url"],
                ),
                (
                    post_id,
                    "backdrop_hotlink",
                    post_data["fondo_player"],
                ),
            ]

            if "rating" in post_data.keys():
                postmeta_data.append((post_id, "rating", post_data["rating"]))

            tvseries_postmeta_data = [
                (
                    post_id,
                    "number_of_seasons",
                    "0",
                ),
                (
                    post_id,
                    "number_of_episodes",
                    "0",
                ),
            ]
            movie_postmeta_data = []

            if "annee" in post_data.keys():
                annee = (
                    post_id,
                    "field_date",
                    post_data["annee"][0],
                )

                tvseries_postmeta_data.append(annee)
                movie_postmeta_data.append(annee)

            if "field_runtime" in post_data.keys():
                tvseries_postmeta_data.append(
                    (
                        post_id,
                        "field_runtime",
                        "a:1:{i:0;i:" + post_data["field_runtime"] + ";}",
                    )
                )

                movie_postmeta_data.append(
                    (post_id, "field_runtime", f"{post_data['field_runtime']}m"),
                )

            if post_data["post_type"] == "series":
                postmeta_data.extend(tvseries_postmeta_data)
            else:
                postmeta_data.extend(movie_postmeta_data)

            self.insert_postmeta(postmeta_data)

            for taxonomy in CONFIG.TAXONOMIES[post_data["post_type"]]:
                if taxonomy in post_data.keys() and post_data[taxonomy]:
                    self.insert_terms(
                        post_id=post_id, terms=post_data[taxonomy], taxonomy=taxonomy
                    )

            return post_id
        except Exception as e:
            self.error_log(
                f"Failed to insert film\n{e}", log_file="toroplay.insert_film.log"
            )

    def format_condition_str(self, equal_condition: str) -> str:
        return equal_condition.replace("\n", "").strip().lower()

    def insert_terms(
        self,
        post_id: int,
        terms: str,
        taxonomy: str,
        is_title: str = False,
        term_slug: str = "",
    ):
        terms = [term.strip() for term in terms.split(",")] if not is_title else [terms]
        termIds = []
        for term in terms:
            term_slug = slugify(term_slug) if term_slug else slugify(term)
            cols = "tt.term_taxonomy_id, tt.term_id"
            table = (
                f"{CONFIG.TABLE_PREFIX}term_taxonomy tt, {CONFIG.TABLE_PREFIX}terms t"
            )
            condition = f't.slug = "{term_slug}" AND tt.term_id=t.term_id AND tt.taxonomy="{taxonomy}"'

            be_term = database.select_all_from(
                table=table, condition=condition, cols=cols
            )
            if not be_term:
                term_id = database.insert_into(
                    table=f"{CONFIG.TABLE_PREFIX}terms",
                    data=(term, term_slug, 0),
                )
                term_taxonomy_count = 1 if taxonomy == "seasons" else 0
                term_taxonomy_id = database.insert_into(
                    table=f"{CONFIG.TABLE_PREFIX}term_taxonomy",
                    data=(term_id, taxonomy, "", 0, term_taxonomy_count),
                )
                termIds = [term_taxonomy_id, True]
            else:
                term_taxonomy_id = be_term[0][0]
                term_id = be_term[0][1]
                termIds = [term_taxonomy_id, False]

            try:
                database.insert_into(
                    table=f"{CONFIG.TABLE_PREFIX}term_relationships",
                    data=(post_id, term_taxonomy_id, 0),
                )
            except:
                pass

        return termIds


helper = ToroplayHelper()


class Toroplay:
    def __init__(self, film: dict, film_links: dict):
        self.film = film
        self.film["quality"] = self.film["extra_info"].get("Qualité", "HD")
        self.film_links = film_links

    def insert_movie_details(self, post_id):
        if not self.film_links:
            return

        logging.info("Inserting movie players")

        quality = self.film["quality"]
        len_episode_links = 0
        postmeta_data = []

        for server_name, server_links in self.film_links.items():
            for language, link in server_links.items():
                if link:
                    postmeta_data.append(
                        (
                            post_id,
                            f"trglinks_{len_episode_links}",
                            helper.generate_trglinks(
                                server=server_name,
                                link=link,
                                lang=language,
                                quality=server_name,
                            ),
                        )
                    )
                    len_episode_links += 1

        postmeta_data.append((post_id, "trgrabber_tlinks", len_episode_links))
        helper.insert_postmeta(postmeta_data)

    def insert_root_film(self) -> list:
        condition_post_name = slugify(self.film["post_title"])
        condition = f"""post_name = '{condition_post_name}' AND post_type='{self.film["post_type"]}'"""
        be_post = database.select_all_from(
            table=f"{CONFIG.TABLE_PREFIX}posts", condition=condition
        )
        if not be_post:
            logging.info(f'Inserting root film: {self.film["post_title"]}')
            post_data = helper.generate_film_data(
                self.film["post_title"],
                self.film["description"],
                self.film["post_type"],
                self.film["trailer_id"],
                self.film["fondo_player"],
                self.film["poster_url"],
                self.film["extra_info"],
            )

            return [helper.insert_film(post_data), True]
        else:
            return [be_post[0][0], False]

    def update_meta_for_post_or_term(
        self, table, condition, new_meta_value, adding: bool = False
    ):
        try:
            be_meta_value = database.select_all_from(
                table=table,
                condition=condition,
                cols="meta_value",
            )[0][0]

            if adding:
                new_meta_value = str(int(new_meta_value) + int(be_meta_value))

            if int(be_meta_value) < int(new_meta_value):
                database.update_table(
                    table=table,
                    set_cond=f"meta_value={new_meta_value}",
                    where_cond=condition,
                )
        except Exception as e:
            helper.error_log(
                msg=f"Error while update_season_number_of_episodes\nSeason {condition} - Number of episodes {new_meta_value}\n{e}",
                log_file="torotheme.update_season_number_of_episodes.log",
            )

    def format_serie_film_links(self):
        new_film_links = {}
        for episode_title, episode_links in self.film_links.items():
            is_has_link = False
            for server, link in episode_links.items():
                if link:
                    is_has_link = True
                    break

            if not is_has_link:
                continue

            (
                episode_title,
                language,
                episode_number,
            ) = helper.get_episode_title_and_language_and_number(
                episode_title=episode_title
            )
            if not episode_number:
                continue

            new_film_links.setdefault(episode_number, {})
            new_film_links[episode_number]["title"] = episode_title

            new_film_links[episode_number].setdefault("video_links", {})
            new_film_links[episode_number]["video_links"][language] = episode_links

        return new_film_links

    def insert_episodes(self, post_id: int, season_term_id: int):
        self.film_links = self.format_serie_film_links()
        len_episodes = 0

        for episode_number, episode in self.film_links.items():
            episode_title = episode.get("title", "")

            episode_term_name = (
                self.film["post_title"]
                + f' {self.film["season_number"]}x{episode_number}'
            )
            episode_term_slug = (
                self.film["post_title"]
                + f'-{self.film["season_number"]}x{episode_number}'
            )
            episode_term_id, is_new_episode = helper.insert_terms(
                post_id=post_id,
                terms=episode_term_name,
                taxonomy="episodes",
                is_title=True,
                term_slug=episode_term_slug,
            )

            if not is_new_episode:
                continue

            len_episode_links = 0
            logging.info(f"Inserting new episode: {episode_title}")

            termmeta_data = [
                (episode_term_id, "episode_number", episode_number),
                (episode_term_id, "name", episode_title),
                (episode_term_id, "season_number", self.film["season_number"]),
                (episode_term_id, "tr_id_post", post_id),
                (episode_term_id, "still_path_hotlink", self.film["poster_url"]),
            ]

            quality = self.film.get("quality", "HD")

            episode_links = episode.get("video_links")
            for language, server_links in episode_links.items():
                for server_name, link in server_links.items():
                    termmeta_data.append(
                        (
                            episode_term_id,
                            f"trglinks_{len_episode_links}",
                            helper.generate_trglinks(
                                server=server_name,
                                link=link,
                                lang=language,
                                quality=server_name,
                            ),
                        )
                    )
                    len_episode_links += 1

            termmeta_data.append(
                (episode_term_id, "trgrabber_tlinks", len_episode_links)
            )

            helper.insert_postmeta(termmeta_data, "termmeta")

            len_episodes += len_episode_links > 0

        table = f"{CONFIG.TABLE_PREFIX}termmeta"
        condition = f"term_id={season_term_id} AND meta_key='number_of_episodes'"
        self.update_meta_for_post_or_term(table, condition, len_episodes)

        table = f"{CONFIG.TABLE_PREFIX}postmeta"
        condition = f"post_id={post_id} AND meta_key='number_of_episodes'"
        self.update_meta_for_post_or_term(table, condition, len_episodes, adding=True)

    def insert_season(self, post_id: int):
        season_term_name = (
            self.film["post_title"] + " - Saison " + self.film["season_number"]
        )
        season_term_slug = self.film["post_title"] + " - " + self.film["season_number"]
        season_term_id, isNewSeason = helper.insert_terms(
            post_id=post_id,
            terms=season_term_name,
            taxonomy="seasons",
            is_title=True,
            term_slug=season_term_slug,
        )

        termmeta_data = [
            (season_term_id, "number_of_episodes", "0"),
            (season_term_id, "name", "Saison " + self.film["season_number"]),
            (season_term_id, "overview", ""),
            (season_term_id, "tr_id_post", post_id),
            (season_term_id, "poster_path_hotlink", self.film["poster_url"]),
            (season_term_id, "season_number", self.film["season_number"]),
        ]

        if isNewSeason:
            logging.info(f"Inserted new season: {season_term_name}")
            helper.insert_postmeta(termmeta_data, "termmeta")

            table = f"{CONFIG.TABLE_PREFIX}postmeta"
            condition = f"post_id={post_id} AND meta_key='number_of_seasons'"
            self.update_meta_for_post_or_term(
                table, condition, self.film["season_number"]
            )

        return season_term_id

    def insert_film(self):
        (
            self.film["post_title"],
            self.film["season_number"],
        ) = helper.get_title_and_season_number(self.film["title"])

        post_id, isNewPostInserted = self.insert_root_film()

        if self.film["post_type"] != "series":
            if isNewPostInserted:
                self.insert_movie_details(post_id)
        else:
            # pass
            season_term_id = self.insert_season(post_id)
            self.insert_episodes(post_id, season_term_id)

        sleep(1)
