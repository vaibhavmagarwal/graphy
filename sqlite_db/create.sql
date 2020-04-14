CREATE TABLE GRAPHY(
   id INTEGER PRIMARY KEY  AUTOINCREMENT,
   title           TEXT    NOT NULL,
   image_path      TEXT    NOT NULL
);

CREATE TABLE CHAPTER(
   id INTEGER PRIMARY KEY AUTOINCREMENT,
   heading      TEXT           NOT NULL,
   description  TEXT,
   video_path   TEXT,
   graphy_id    INTEGER        NOT NULL,
   FOREIGN KEY (graphy_id)
            REFERENCES GRAPHY(id)
);