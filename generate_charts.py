import os
import sqlite3
from collections import defaultdict

import matplotlib.pyplot as plt
import pandas as pd

# ==============================
# CONFIGURAÇÃO
# ==============================

DB_PATH = r"C:\Users\Diogo\Documents\GitHub\Mythology-in-Digital-Games\data\sqlite\mythology_in_digital_games.db"
OUTPUT_GLOBAL = os.path.join("charts", "global")
OUTPUT_BY_MYTH = os.path.join("charts", "by_myth")

os.makedirs(OUTPUT_GLOBAL, exist_ok=True)
os.makedirs(OUTPUT_BY_MYTH, exist_ok=True)


def get_conn():
    return sqlite3.connect(DB_PATH)


def safe_myth_dir_name(name: str) -> str:
    """
    Cria um nome de pasta seguro a partir do nome da mitologia.
    """
    safe = "".join(c if c.isalnum() or c in " _-" else "_" for c in name)
    safe = safe.strip()
    safe = safe.replace(" ", "_")
    return safe or "Unknown"


# ==============================
# GRÁFICOS GERAIS
# ==============================

def chart_global_myth_distribution():
    """
    Pie chart de distribuição geral de jogos por mitologia (todas as mitologias),
    ordenado do que aparece mais vezes para o que aparece menos.
    """
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            m.name,
            COUNT(DISTINCT gm.game_id) AS num_games
        FROM mythologies m
        LEFT JOIN game_mythologies gm ON gm.mythology_id = m.id
        GROUP BY m.id, m.name
        ORDER BY num_games DESC, m.name;
    """)
    rows = cur.fetchall()
    conn.close()

    if not rows:
        print("Sem dados para o gráfico global de mitologias.")
        return

    labels = [r[0] for r in rows]
    sizes = [r[1] for r in rows]

    total = sum(sizes)
    if total == 0:
        print("Todas as mitologias têm 0 jogos, nada a desenhar.")
        return

    fig, ax = plt.subplots(figsize=(10, 10))

    wedges, _ = ax.pie(sizes, startangle=90)
    ax.axis('equal')

    labels_with_vals = [
        f"{name} ({value} jogos, {value/total:.1%})"
        for name, value in zip(labels, sizes)
    ]

    ax.legend(
        wedges,
        labels_with_vals,
        title="Mitologias (mais → menos jogos)",
        loc="center left",
        bbox_to_anchor=(1, 0.5),
        fontsize=5
    )

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_GLOBAL, "global_myth_distribution_pie.png")
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("→ Gerado:", out_path)


def chart_global_releases_per_month():
    """
    Linha global de lançamentos por mês (jogos com mitologia).
    """
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            strftime('%Y-%m', g.release_date) AS ym,
            COUNT(DISTINCT g.id) AS num_games
        FROM games g
        JOIN game_mythologies gm ON gm.game_id = g.id
        WHERE g.release_date IS NOT NULL
        GROUP BY ym
        ORDER BY ym;
    """)
    rows = cur.fetchall()
    conn.close()

    if not rows:
        print("Sem dados para lançamentos globais por mês.")
        return

    months = [r[0] for r in rows]
    counts = [r[1] for r in rows]

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(months, counts, marker='o')
    ax.set_title("Lançamentos de jogos com mitologia por mês")
    ax.set_xlabel("Ano-Mês")
    ax.set_ylabel("Nº de jogos")

    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    out_path = os.path.join(OUTPUT_GLOBAL, "global_releases_per_month.png")
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("→ Gerado:", out_path)


def chart_heatmap_myth_genre_primary():
    """
    Heatmap mitologia × género PRINCIPAL (gg.is_primary = 1).
    """
    conn = get_conn()

    df = pd.read_sql_query("""
        SELECT 
            m.name AS mythology,
            g2.name AS genre,
            COUNT(DISTINCT gm.game_id) AS num_games
        FROM game_mythologies gm
        JOIN mythologies   m  ON gm.mythology_id = m.id
        JOIN game_genres   gg ON gm.game_id      = gg.game_id
        JOIN genres        g2 ON gg.genre_id     = g2.id
        WHERE gg.is_primary = 1
        GROUP BY m.id, g2.id;
    """, conn)

    conn.close()

    if df.empty:
        print("Sem dados para heatmap mitologia × género principal.")
        return

    pivot = df.pivot(index="mythology", columns="genre", values="num_games").fillna(0)

    fig, ax = plt.subplots(figsize=(12, 12))
    cax = ax.imshow(pivot.values, aspect='auto')

    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, rotation=45, ha='right', fontsize=6)

    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index, fontsize=5)

    ax.set_xlabel("Género principal")
    ax.set_ylabel("Mitologia")
    ax.set_title("Heatmap: Mitologia × Género principal")

    fig.colorbar(cax, ax=ax, label="Nº de jogos")
    plt.tight_layout()

    out_path = os.path.join(OUTPUT_GLOBAL, "heatmap_myth_genre_primary.png")
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("→ Gerado:", out_path)


def chart_heatmap_myth_genre_all():
    """
    Heatmap mitologia × TODOS os géneros (principal + secundários).
    """
    conn = get_conn()

    df = pd.read_sql_query("""
        SELECT 
            m.name AS mythology,
            g2.name AS genre,
            COUNT(DISTINCT gm.game_id) AS num_games
        FROM game_mythologies gm
        JOIN mythologies   m  ON gm.mythology_id = m.id
        JOIN game_genres   gg ON gm.game_id      = gg.game_id
        JOIN genres        g2 ON gg.genre_id     = g2.id
        GROUP BY m.id, g2.id;
    """, conn)

    conn.close()

    if df.empty:
        print("Sem dados para heatmap mitologia × todos os géneros.")
        return

    pivot = df.pivot(index="mythology", columns="genre", values="num_games").fillna(0)

    fig, ax = plt.subplots(figsize=(12, 12))
    cax = ax.imshow(pivot.values, aspect='auto')

    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, rotation=45, ha='right', fontsize=6)

    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index, fontsize=5)

    ax.set_xlabel("Género (todos)")
    ax.set_ylabel("Mitologia")
    ax.set_title("Heatmap: Mitologia × Todos os géneros")

    fig.colorbar(cax, ax=ax, label="Nº de jogos")
    plt.tight_layout()

    out_path = os.path.join(OUTPUT_GLOBAL, "heatmap_myth_genre_all.png")
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("→ Gerado:", out_path)


def chart_heatmap_myth_country():
    """
    Heatmap mitologia × país do estúdio.
    """
    conn = get_conn()

    df = pd.read_sql_query("""
        SELECT 
            m.name AS mythology,
            s.country_code AS country,
            COUNT(DISTINCT gm.game_id) AS num_games
        FROM game_mythologies gm
        JOIN mythologies m ON gm.mythology_id = m.id
        JOIN game_studios gs ON gm.game_id    = gs.game_id
        JOIN studios     s  ON gs.studio_id   = s.id
        GROUP BY m.id, s.country_code;
    """, conn)

    conn.close()

    if df.empty:
        print("Sem dados para heatmap mitologia × país.")
        return

    pivot = df.pivot(index="mythology", columns="country", values="num_games").fillna(0)

    fig, ax = plt.subplots(figsize=(12, 12))
    cax = ax.imshow(pivot.values, aspect='auto')

    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, rotation=45, ha='right', fontsize=6)

    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index, fontsize=5)

    ax.set_xlabel("País do estúdio")
    ax.set_ylabel("Mitologia")
    ax.set_title("Heatmap: Mitologia × País do estúdio")

    fig.colorbar(cax, ax=ax, label="Nº de jogos")
    plt.tight_layout()

    out_path = os.path.join(OUTPUT_GLOBAL, "heatmap_myth_country.png")
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("→ Gerado:", out_path)


def chart_games_by_myth_count():
    """
    Barras “nº de jogos com X mitologias” (1, 2, 3+).
    """
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT cnt_myths, COUNT(*) AS num_games
        FROM (
            SELECT game_id, COUNT(DISTINCT mythology_id) AS cnt_myths
            FROM game_mythologies
            GROUP BY game_id
        ) t
        GROUP BY cnt_myths
        ORDER BY cnt_myths;
    """)
    rows = cur.fetchall()
    conn.close()

    if not rows:
        print("Sem dados para jogos por nº de mitologias.")
        return

    buckets = defaultdict(int)
    for cnt_myths, num_games in rows:
        if cnt_myths <= 2:
            buckets[cnt_myths] += num_games
        else:
            buckets[3] += num_games  # 3+

    labels = ["1", "2", "3+"]
    values = [buckets[1], buckets[2], buckets[3]]

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(labels, values)
    ax.set_xlabel("Nº de mitologias por jogo")
    ax.set_ylabel("Nº de jogos")
    ax.set_title("Distribuição de jogos por nº de mitologias")

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_GLOBAL, "games_by_myth_count.png")
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("→ Gerado:", out_path)


def chart_global_platform_distribution():
    """
    Barras: nº de jogos por plataforma (jogos com mitologia).
    Cada jogo conta uma vez por plataforma em que existe.
    """
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            p.name AS platform,
            COUNT(DISTINCT gp.game_id) AS num_games
        FROM platforms p
        JOIN game_platforms gp ON gp.platform_id = p.id
        JOIN game_mythologies gm ON gm.game_id   = gp.game_id
        GROUP BY p.id, p.name
        ORDER BY num_games DESC;
    """)
    rows = cur.fetchall()
    conn.close()

    if not rows:
        print("Sem dados para distribuição global por plataforma.")
        return

    platforms = [r[0] for r in rows]
    counts = [r[1] for r in rows]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(platforms, counts)
    ax.set_title("Distribuição de jogos por plataforma (jogos com mitologia)")
    ax.set_xlabel("Plataforma")
    ax.set_ylabel("Nº de jogos")

    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    out_path = os.path.join(OUTPUT_GLOBAL, "global_platform_distribution.png")
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("→ Gerado:", out_path)


# ==============================
# GRÁFICOS POR MITOLOGIA
# ==============================

def charts_by_myth_timelines():
    """
    Linha de lançamentos por mês para cada mitologia.
    Gera um PNG por mitologia: timeline.png dentro da pasta da mitologia.
    """
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT id, name FROM mythologies ORDER BY name;")
    myths = cur.fetchall()

    for myth_id, myth_name in myths:
        cur.execute("""
            SELECT 
                strftime('%Y-%m', g.release_date) AS ym,
                COUNT(DISTINCT g.id) AS num_games
            FROM games g
            JOIN game_mythologies gm ON gm.game_id = g.id
            WHERE gm.mythology_id = ?
              AND g.release_date IS NOT NULL
            GROUP BY ym
            ORDER BY ym;
        """, (myth_id,))
        rows = cur.fetchall()

        if not rows:
            continue

        months = [r[0] for r in rows]
        counts = [r[1] for r in rows]

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(months, counts, marker='o')
        ax.set_title(f"Lançamentos por mês – {myth_name}")
        ax.set_xlabel("Ano-Mês")
        ax.set_ylabel("Nº de jogos")

        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        myth_dir = os.path.join(OUTPUT_BY_MYTH, safe_myth_dir_name(myth_name))
        os.makedirs(myth_dir, exist_ok=True)
        out_path = os.path.join(myth_dir, "timeline.png")
        plt.savefig(out_path, dpi=200, bbox_inches="tight")
        plt.close(fig)
        print("→ Gerado:", out_path)

    conn.close()


def charts_by_myth_genre_distribution_primary():
    """
    Para cada mitologia, gráfico de barras com distribuição de géneros
    PRINCIPAIS (gg.is_primary = 1).
    Guarda em <Mitologia>/genres_primary.png
    """
    conn = get_conn()

    df = pd.read_sql_query("""
        SELECT 
            m.id   AS myth_id,
            m.name AS myth_name,
            g2.name AS genre,
            COUNT(DISTINCT gm.game_id) AS num_games
        FROM game_mythologies gm
        JOIN mythologies m ON gm.mythology_id = m.id
        JOIN game_genres gg ON gm.game_id     = gg.game_id
        JOIN genres g2      ON gg.genre_id    = g2.id
        WHERE gg.is_primary = 1
        GROUP BY m.id, g2.id;
    """, conn)

    conn.close()

    if df.empty:
        print("Sem dados para distribuição de géneros principais por mitologia.")
        return

    for myth_id, group in df.groupby("myth_id"):
        myth_name = group["myth_name"].iloc[0]
        genres = group["genre"].tolist()
        counts = group["num_games"].tolist()

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(genres, counts)
        ax.set_title(f"Géneros principais – {myth_name}")
        ax.set_xlabel("Género")
        ax.set_ylabel("Nº de jogos")

        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        myth_dir = os.path.join(OUTPUT_BY_MYTH, safe_myth_dir_name(myth_name))
        os.makedirs(myth_dir, exist_ok=True)
        out_path = os.path.join(myth_dir, "genres_primary.png")
        plt.savefig(out_path, dpi=200, bbox_inches="tight")
        plt.close(fig)
        print("→ Gerado:", out_path)


def charts_by_myth_genre_distribution_all():
    """
    Para cada mitologia, gráfico de barras com distribuição de TODOS os géneros
    (principal + secundários).
    Guarda em <Mitologia>/genres_all.png
    """
    conn = get_conn()

    df = pd.read_sql_query("""
        SELECT 
            m.id   AS myth_id,
            m.name AS myth_name,
            g2.name AS genre,
            COUNT(DISTINCT gm.game_id) AS num_games
        FROM game_mythologies gm
        JOIN mythologies m ON gm.mythology_id = m.id
        JOIN game_genres gg ON gm.game_id     = gg.game_id
        JOIN genres g2      ON gg.genre_id    = g2.id
        GROUP BY m.id, g2.id;
    """, conn)

    conn.close()

    if df.empty:
        print("Sem dados para distribuição de todos os géneros por mitologia.")
        return

    for myth_id, group in df.groupby("myth_id"):
        myth_name = group["myth_name"].iloc[0]
        genres = group["genre"].tolist()
        counts = group["num_games"].tolist()

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(genres, counts)
        ax.set_title(f"Todos os géneros – {myth_name}")
        ax.set_xlabel("Género")
        ax.set_ylabel("Nº de jogos")

        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        myth_dir = os.path.join(OUTPUT_BY_MYTH, safe_myth_dir_name(myth_name))
        os.makedirs(myth_dir, exist_ok=True)
        out_path = os.path.join(myth_dir, "genres_all.png")
        plt.savefig(out_path, dpi=200, bbox_inches="tight")
        plt.close(fig)
        print("→ Gerado:", out_path)


# ----- Interno vs Externo: helpers -----

def _split_region_countries(region_str: str):
    """
    Converte uma string tipo:
      'Noruega, Suécia, Dinamarca, Islândia'
    num set: {'noruega', 'suécia', 'dinamarca', 'islândia'}
    Aceita separadores: vírgula, ponto e vírgula, barra, pipe.
    """
    if region_str is None:
        return set()
    txt = str(region_str).lower()
    for sep in [';', '/', '|']:
        txt = txt.replace(sep, ',')
    parts = [p.strip() for p in txt.split(',')]
    return {p for p in parts if p}


def _charts_by_myth_internal_external_base(role_filter, label_suffix, filename_suffix):
    """
    Gera gráficos Interno vs Externo por mitologia, a contar Nº de ESTÚDIOS,
    com filtro opcional por role (Developer / Publisher / None para todos).

    Suporta mitologias com vários países na coluna mythologies.region:
    ex: 'Noruega, Suécia, Dinamarca, Islândia'.

    Guarda em <Mitologia>/<filename_suffix>.png
    """
    conn = get_conn()

    sql = """
        SELECT 
            m.id   AS myth_id,
            m.name AS myth_name,
            m.region AS myth_region,
            s.country_code AS country_name,
            gs.role AS role,
            COUNT(DISTINCT s.id) AS num_studios
        FROM game_mythologies gm
        JOIN mythologies m ON gm.mythology_id = m.id
        JOIN game_studios gs ON gm.game_id    = gs.game_id
        JOIN studios s      ON gs.studio_id   = s.id
    """
    params = []
    if role_filter is None:
        sql += "GROUP BY m.id, s.country_code;\n"
    else:
        sql += "WHERE gs.role = ?\nGROUP BY m.id, s.country_code;\n"
        params.append(role_filter)

    df = pd.read_sql_query(sql, conn, params=params)
    conn.close()

    if df.empty:
        print(f"Sem dados para interno vs externo ({label_suffix}).")
        return

    records = []
    for _, row in df.iterrows():
        myth_region = row["myth_region"]
        country_name = row["country_name"]

        if myth_region is None or str(myth_region).strip() == "":
            continue
        if country_name is None or str(country_name).strip() == "":
            continue

        myth_countries = _split_region_countries(myth_region)
        country_norm = str(country_name).strip().lower()

        origin_type = "Interno" if country_norm in myth_countries else "Externo"

        records.append({
            "myth_id": row["myth_id"],
            "myth_name": row["myth_name"],
            "origin_type": origin_type,
            "num_studios": row["num_studios"],
        })

    if not records:
        print(f"Sem dados utilizáveis para interno vs externo ({label_suffix}).")
        return

    df2 = pd.DataFrame(records)

    for myth_id, group in df2.groupby("myth_id"):
        myth_name = group["myth_name"].iloc[0]

        interno = group.loc[group["origin_type"] == "Interno", "num_studios"].sum()
        externo = group.loc[group["origin_type"] == "Externo", "num_studios"].sum()

        if interno == 0 and externo == 0:
            continue

        labels = ["Interno", "Externo"]
        values = [interno, externo]

        fig, ax = plt.subplots(figsize=(5, 4))
        ax.bar(labels, values)
        ax.set_title(f"Origem das representações ({label_suffix}) – {myth_name}")
        ax.set_ylabel("Nº de estúdios")

        plt.tight_layout()
        myth_dir = os.path.join(OUTPUT_BY_MYTH, safe_myth_dir_name(myth_name))
        os.makedirs(myth_dir, exist_ok=True)
        out_path = os.path.join(myth_dir, filename_suffix + ".png")
        plt.savefig(out_path, dpi=200, bbox_inches="tight")
        plt.close(fig)
        print("→ Gerado:", out_path)


def charts_by_myth_internal_external_all():
    """
    Interno vs Externo – TODOS os estúdios (qualquer role).
    Guarda em <Mitologia>/internal_external_all.png
    """
    _charts_by_myth_internal_external_base(
        role_filter=None,
        label_suffix="todos os estúdios",
        filename_suffix="internal_external_all"
    )


def charts_by_myth_internal_external_devs():
    """
    Interno vs Externo – só Developers (assume gs.role = 'Developer').
    Guarda em <Mitologia>/internal_external_devs.png
    """
    _charts_by_myth_internal_external_base(
        role_filter="Developer",
        label_suffix="Developers",
        filename_suffix="internal_external_devs"
    )


def charts_by_myth_internal_external_pubs():
    """
    Interno vs Externo – só Publishers (assume gs.role = 'Publisher').
    Guarda em <Mitologia>/internal_external_pubs.png
    """
    _charts_by_myth_internal_external_base(
        role_filter="Publisher",
        label_suffix="Publishers",
        filename_suffix="internal_external_pubs"
    )


def charts_by_myth_platform_distribution():
    """
    Para cada mitologia, gráfico de barras com distribuição de plataformas
    (em que plataformas aparecem os jogos dessa mitologia).
    Guarda em <Mitologia>/platforms.png
    """
    conn = get_conn()

    df = pd.read_sql_query("""
        SELECT 
            m.id   AS myth_id,
            m.name AS myth_name,
            p.name AS platform,
            COUNT(DISTINCT gm.game_id) AS num_games
        FROM game_mythologies gm
        JOIN mythologies   m  ON gm.mythology_id = m.id
        JOIN game_platforms gp ON gp.game_id     = gm.game_id
        JOIN platforms     p  ON gp.platform_id  = p.id
        GROUP BY m.id, p.id;
    """, conn)

    conn.close()

    if df.empty:
        print("Sem dados para distribuição de plataformas por mitologia.")
        return

    for myth_id, group in df.groupby("myth_id"):
        myth_name = group["myth_name"].iloc[0]
        platforms = group["platform"].tolist()
        counts = group["num_games"].tolist()

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(platforms, counts)
        ax.set_title(f"Plataformas – {myth_name}")
        ax.set_xlabel("Plataforma")
        ax.set_ylabel("Nº de jogos")

        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        myth_dir = os.path.join(OUTPUT_BY_MYTH, safe_myth_dir_name(myth_name))
        os.makedirs(myth_dir, exist_ok=True)
        out_path = os.path.join(myth_dir, "platforms.png")
        plt.savefig(out_path, dpi=200, bbox_inches="tight")
        plt.close(fig)
        print("→ Gerado:", out_path)


# ==============================
# MAIN
# ==============================

def main():
    # GERAIS
    chart_global_myth_distribution()
    chart_global_releases_per_month()
    chart_heatmap_myth_genre_primary()
    chart_heatmap_myth_genre_all()
    chart_heatmap_myth_country()
    chart_games_by_myth_count()
    chart_global_platform_distribution()

    # POR MITOLOGIA
    charts_by_myth_timelines()
    charts_by_myth_genre_distribution_primary()
    charts_by_myth_genre_distribution_all()
    charts_by_myth_internal_external_all()
    charts_by_myth_internal_external_devs()
    charts_by_myth_internal_external_pubs()
    charts_by_myth_platform_distribution()


if __name__ == "__main__":
    main()
