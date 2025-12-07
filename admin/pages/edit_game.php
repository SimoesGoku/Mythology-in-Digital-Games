<?php
require_once __DIR__ . '/../config.php';

$game_id = isset($_GET['id']) ? (int)$_GET['id'] : 0;
if (!$game_id) {
    die('ID de jogo inválido.');
}

// Buscar info do jogo
$stmt = $db->prepare('SELECT id, title, release_date FROM games WHERE id = :id');
$stmt->execute([':id' => $game_id]);
$game = $stmt->fetch(PDO::FETCH_ASSOC);

if (!$game) {
    die('Jogo não encontrado.');
}

$mensagem = '';
$action = ($_SERVER['REQUEST_METHOD'] === 'POST') ? ($_POST['action'] ?? 'save_all') : null;

// ------------------------
// POST: tratar ações
// ------------------------
if ($_SERVER['REQUEST_METHOD'] === 'POST') {

    // 1) Criar género novo (não mexe nas ligações do jogo)
    if ($action === 'add_genre') {
        $new_genre_name = trim($_POST['new_genre'] ?? '');
        if ($new_genre_name !== '') {
            try {
                $stmt = $db->prepare('INSERT INTO genres (name) VALUES (:name)');
                $stmt->execute([':name' => $new_genre_name]);
                $mensagem = 'Género criado com sucesso.';
            } catch (PDOException $e) {
                $mensagem = 'Erro ao criar género (pode já existir): ' . $e->getMessage();
            }
        } else {
            $mensagem = 'Nome do género está vazio.';
        }
    }

    // 2) Criar estúdio como Developer
    if ($action === 'add_dev') {
        $new_dev_name    = trim($_POST['new_dev_name'] ?? '');
        $new_dev_country = trim($_POST['new_dev_country'] ?? '');
        if ($new_dev_name !== '') {
            $stmt = $db->prepare('INSERT INTO studios (name, country_code) VALUES (:name, :country)');
            $stmt->execute([
                ':name'    => $new_dev_name,
                ':country' => $new_dev_country !== '' ? $new_dev_country : null,
            ]);
            $mensagem = 'Estúdio (Developer) criado com sucesso.';
        } else {
            $mensagem = 'Nome do estúdio (Developer) está vazio.';
        }
    }

    // 3) Criar estúdio como Publisher
    if ($action === 'add_pub') {
        $new_pub_name    = trim($_POST['new_pub_name'] ?? '');
        $new_pub_country = trim($_POST['new_pub_country'] ?? '');
        if ($new_pub_name !== '') {
            $stmt = $db->prepare('INSERT INTO studios (name, country_code) VALUES (:name, :country)');
            $stmt->execute([
                ':name'    => $new_pub_name,
                ':country' => $new_pub_country !== '' ? $new_pub_country : null,
            ]);
            $mensagem = 'Estúdio (Publisher) criado com sucesso.';
        } else {
            $mensagem = 'Nome do estúdio (Publisher) está vazio.';
        }
    }

    // 4) Guardar tudo (jogo + ligações)
    if ($action === 'save_all') {
        $title = trim($_POST['title'] ?? '');
        $release_date = trim($_POST['release_date'] ?? '');

        if ($title === '') {
            $mensagem = 'Título não pode ser vazio.';
        } else {
            // Atualizar dados base
            $stmt = $db->prepare('UPDATE games SET title = :title, release_date = :release_date WHERE id = :id');
            $stmt->execute([
                ':title'        => $title,
                ':release_date' => $release_date !== '' ? $release_date : null,
                ':id'           => $game_id,
            ]);
            $game['title'] = $title;
            $game['release_date'] = $release_date !== '' ? $release_date : null;

            // Ler selecções do formulário
            $selected_mythologies = array_map('intval', $_POST['mythologies'] ?? []);
            $selected_genres      = array_map('intval', $_POST['genres'] ?? []);
            $primary_genre        = isset($_POST['primary_genre']) ? (int)$_POST['primary_genre'] : 0;
            $selected_platforms   = array_map('intval', $_POST['platforms'] ?? []);
            $selected_devs        = array_map('intval', $_POST['studios_developer'] ?? []);
            $selected_pubs        = array_map('intval', $_POST['studios_publisher'] ?? []);

            // Garantir que o género principal está incluído
            if ($primary_genre !== 0 && !in_array($primary_genre, $selected_genres, true)) {
                $selected_genres[] = $primary_genre;
            }

            // Mitologias
            $db->prepare('DELETE FROM game_mythologies WHERE game_id = :id')
               ->execute([':id' => $game_id]);

            $stmtInsertGM = $db->prepare('INSERT INTO game_mythologies (game_id, mythology_id) VALUES (:g, :m)');
            foreach ($selected_mythologies as $mid) {
                $stmtInsertGM->execute([':g' => $game_id, ':m' => $mid]);
            }

            // Géneros
            $db->prepare('DELETE FROM game_genres WHERE game_id = :id')
               ->execute([':id' => $game_id]);

            $stmtInsertGG = $db->prepare('INSERT INTO game_genres (game_id, genre_id, is_primary) VALUES (:g, :genre, :primary)');
            foreach ($selected_genres as $gid) {
                $is_primary = ($primary_genre === $gid) ? 1 : 0;
                $stmtInsertGG->execute([
                    ':g'       => $game_id,
                    ':genre'   => $gid,
                    ':primary' => $is_primary,
                ]);
            }

            // Plataformas
            $db->prepare('DELETE FROM game_platforms WHERE game_id = :id')
               ->execute([':id' => $game_id]);

            $stmtInsertGP = $db->prepare('INSERT INTO game_platforms (game_id, platform_id) VALUES (:g, :p)');
            foreach ($selected_platforms as $pid) {
                $stmtInsertGP->execute([':g' => $game_id, ':p' => $pid]);
            }

            // Estúdios
            $db->prepare('DELETE FROM game_studios WHERE game_id = :id')
               ->execute([':id' => $game_id]);

            $stmtInsertGS = $db->prepare('INSERT INTO game_studios (game_id, studio_id, role) VALUES (:g, :s, :r)');

            foreach ($selected_devs as $sid) {
                $stmtInsertGS->execute([
                    ':g' => $game_id,
                    ':s' => $sid,
                    ':r' => 'Developer',
                ]);
            }

            foreach ($selected_pubs as $sid) {
                $stmtInsertGS->execute([
                    ':g' => $game_id,
                    ':s' => $sid,
                    ':r' => 'Publisher',
                ]);
            }

            $mensagem = 'Jogo e ligações atualizados.';
        }
    }

    // Manter título/data escritos mesmo quando não é "save_all"
    if ($action !== 'save_all') {
        if (isset($_POST['title'])) {
            $game['title'] = $_POST['title'];
        }
        if (isset($_POST['release_date'])) {
            $game['release_date'] = $_POST['release_date'] !== '' ? $_POST['release_date'] : null;
        }
    }
}

// ------------------------
// Buscar listas base (sempre da BD)
// ------------------------
$all_mythologies = $db->query('SELECT id, name FROM mythologies ORDER BY name')->fetchAll(PDO::FETCH_ASSOC);
$all_genres      = $db->query('SELECT id, name FROM genres ORDER BY name')->fetchAll(PDO::FETCH_ASSOC);
$all_platforms   = $db->query('SELECT id, name FROM platforms ORDER BY name')->fetchAll(PDO::FETCH_ASSOC);
$all_studios     = $db->query('SELECT id, name FROM studios ORDER BY name')->fetchAll(PDO::FETCH_ASSOC);

// ------------------------
// Estado selecionado: POST (para add_*) ou BD (save_all / GET)
// ------------------------
if ($_SERVER['REQUEST_METHOD'] === 'POST' && $action !== 'save_all') {
    // Usar o que veio do formulário
    $current_myth_ids      = array_map('intval', $_POST['mythologies'] ?? []);
    $current_genre_ids     = array_map('intval', $_POST['genres'] ?? []);
    $current_primary_genre = isset($_POST['primary_genre']) ? (int)$_POST['primary_genre'] : 0;
    $current_platform_ids  = array_map('intval', $_POST['platforms'] ?? []);
    $current_devs          = array_map('intval', $_POST['studios_developer'] ?? []);
    $current_pubs          = array_map('intval', $_POST['studios_publisher'] ?? []);
} else {
    // Usar o que está em BD
    $stmt = $db->prepare('SELECT mythology_id FROM game_mythologies WHERE game_id = :id');
    $stmt->execute([':id' => $game_id]);
    $current_myth_ids = array_map('intval', $stmt->fetchAll(PDO::FETCH_COLUMN));

    $stmt = $db->prepare('SELECT genre_id, is_primary FROM game_genres WHERE game_id = :id');
    $stmt->execute([':id' => $game_id]);
    $rowsGenres = $stmt->fetchAll(PDO::FETCH_ASSOC);
    $current_genre_ids = [];
    $current_primary_genre = 0;
    foreach ($rowsGenres as $row) {
        $gid = (int)$row['genre_id'];
        $current_genre_ids[] = $gid;
        if ((int)$row['is_primary'] === 1) {
            $current_primary_genre = $gid;
        }
    }

    $stmt = $db->prepare('SELECT platform_id FROM game_platforms WHERE game_id = :id');
    $stmt->execute([':id' => $game_id]);
    $current_platform_ids = array_map('intval', $stmt->fetchAll(PDO::FETCH_COLUMN));

    $stmt = $db->prepare('SELECT studio_id, role FROM game_studios WHERE game_id = :id');
    $stmt->execute([':id' => $game_id]);
    $current_devs = [];
    $current_pubs = [];
    foreach ($stmt->fetchAll(PDO::FETCH_ASSOC) as $row) {
        if ($row['role'] === 'Developer') {
            $current_devs[] = (int)$row['studio_id'];
        } elseif ($row['role'] === 'Publisher') {
            $current_pubs[] = (int)$row['studio_id'];
        }
    }
}
?>
<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <title>Editar jogo – <?= htmlspecialchars($game['title']) ?></title>
    <script>
        function moveSelected(fromId, toId) {
            const from = document.getElementById(fromId);
            const to = document.getElementById(toId);
            if (!from || !to) return;
            const toMove = [];
            for (let i = 0; i < from.options.length; i++) {
                const opt = from.options[i];
                if (opt.selected) {
                    toMove.push(opt);
                }
            }
            toMove.forEach(opt => {
                opt.selected = false;
                to.appendChild(opt);
            });
        }

        function selectAll(id) {
            const sel = document.getElementById(id);
            if (!sel) return;
            for (let i = 0; i < sel.options.length; i++) {
                sel.options[i].selected = true;
            }
        }

        function beforeSubmit() {
            selectAll('myths_selected');
            selectAll('genres_selected');
            selectAll('platforms_selected');
            selectAll('studios_dev_selected');
            selectAll('studios_pub_selected');
            return true;
        }
    </script>
</head>
<body>
    <h1>Editar jogo</h1>
    <p><a href="list_games.php">← Voltar à lista</a></p>

    <?php if ($mensagem): ?>
        <p><strong><?= htmlspecialchars($mensagem) ?></strong></p>
    <?php endif; ?>

    <form method="post" onsubmit="return beforeSubmit();">
        <fieldset>
            <legend>Dados base</legend>
            <label>
                Título:<br>
                <input type="text" name="title" value="<?= htmlspecialchars($game['title']) ?>" required>
            </label>
            <br><br>
            <label>
                Data de lançamento (YYYY ou YYYY-MM-DD):<br>
                <input type="text" name="release_date" value="<?= htmlspecialchars($game['release_date'] ?? '') ?>">
            </label>
        </fieldset>

        <br>

        <!-- MITOLOGIAS -->
        <fieldset>
            <legend>Mitologias deste jogo</legend>
            <?php if (empty($all_mythologies)): ?>
                <p>Não há mitologias na base de dados. Insere primeiro via DB Browser / CSV.</p>
            <?php else: ?>
                <table>
                    <tr>
                        <td>
                            <strong>Disponíveis</strong><br>
                            <select id="myths_available" multiple size="12">
                                <?php foreach ($all_mythologies as $m): ?>
                                    <?php if (!in_array((int)$m['id'], $current_myth_ids, true)): ?>
                                        <option value="<?= (int)$m['id'] ?>">
                                            <?= htmlspecialchars($m['name']) ?>
                                        </option>
                                    <?php endif; ?>
                                <?php endforeach; ?>
                            </select>
                        </td>
                        <td style="padding: 0 10px; vertical-align: middle;">
                            <button type="button" onclick="moveSelected('myths_available', 'myths_selected')">
                                &gt;&gt;
                            </button>
                            <br><br>
                            <button type="button" onclick="moveSelected('myths_selected', 'myths_available')">
                                &lt;&lt;
                            </button>
                        </td>
                        <td>
                            <strong>Selecionadas</strong><br>
                            <select name="mythologies[]" id="myths_selected" multiple size="12">
                                <?php foreach ($all_mythologies as $m): ?>
                                    <?php if (in_array((int)$m['id'], $current_myth_ids, true)): ?>
                                        <option value="<?= (int)$m['id'] ?>">
                                            <?= htmlspecialchars($m['name']) ?>
                                        </option>
                                    <?php endif; ?>
                                <?php endforeach; ?>
                            </select>
                        </td>
                    </tr>
                </table>
                <p><small>Usa &gt;&gt; / &lt;&lt; para mover entre listas.</small></p>
            <?php endif; ?>
        </fieldset>

        <br>

        <!-- GÉNEROS -->
        <fieldset>
            <legend>Géneros deste jogo</legend>

            <table>
                <tr>
                    <td>
                        <strong>Disponíveis</strong><br>
                        <select id="genres_available" multiple size="8">
                            <?php foreach ($all_genres as $g): ?>
                                <?php if (!in_array((int)$g['id'], $current_genre_ids, true)): ?>
                                    <option value="<?= (int)$g['id'] ?>">
                                        <?= htmlspecialchars($g['name']) ?>
                                    </option>
                                <?php endif; ?>
                            <?php endforeach; ?>
                        </select>
                    </td>
                    <td style="padding: 0 10px; vertical-align: middle;">
                        <button type="button" onclick="moveSelected('genres_available', 'genres_selected')">
                            &gt;&gt;
                        </button>
                        <br><br>
                        <button type="button" onclick="moveSelected('genres_selected', 'genres_available')">
                            &lt;&lt;
                        </button>
                    </td>
                    <td>
                        <strong>Selecionados</strong><br>
                        <select name="genres[]" id="genres_selected" multiple size="8">
                            <?php foreach ($all_genres as $g): ?>
                                <?php if (in_array((int)$g['id'], $current_genre_ids, true)): ?>
                                    <option value="<?= (int)$g['id'] ?>">
                                        <?= htmlspecialchars($g['name']) ?>
                                    </option>
                                <?php endif; ?>
                            <?php endforeach; ?>
                        </select>
                    </td>
                </tr>
            </table>

            <p><small>Podes associar vários géneros. O principal é escolhido abaixo.</small></p>

            <label>
                Criar novo género (apenas cria na BD, não guarda automaticamente ligações):<br>
                <input type="text" name="new_genre" placeholder="ex: Action RPG">
            </label>
            <button type="submit" name="action" value="add_genre">Criar género</button>
        </fieldset>

        <br>

        <!-- PLATAFORMAS -->
        <fieldset>
            <legend>Plataformas onde o jogo existe</legend>
            <?php if (empty($all_platforms)): ?>
                <p>Não há plataformas. Insere-as diretamente na tabela `platforms`.</p>
            <?php else: ?>
                <table>
                    <tr>
                        <td>
                            <strong>Disponíveis</strong><br>
                            <select id="platforms_available" multiple size="8">
                                <?php foreach ($all_platforms as $p): ?>
                                    <?php if (!in_array((int)$p['id'], $current_platform_ids, true)): ?>
                                        <option value="<?= (int)$p['id'] ?>">
                                            <?= htmlspecialchars($p['name']) ?>
                                        </option>
                                    <?php endif; ?>
                                <?php endforeach; ?>
                            </select>
                        </td>
                        <td style="padding: 0 10px; vertical-align: middle;">
                            <button type="button" onclick="moveSelected('platforms_available', 'platforms_selected')">
                                &gt;&gt;
                            </button>
                            <br><br>
                            <button type="button" onclick="moveSelected('platforms_selected', 'platforms_available')">
                                &lt;&lt;
                            </button>
                        </td>
                        <td>
                            <strong>Selecionadas</strong><br>
                            <select name="platforms[]" id="platforms_selected" multiple size="8">
                                <?php foreach ($all_platforms as $p): ?>
                                    <?php if (in_array((int)$p['id'], $current_platform_ids, true)): ?>
                                        <option value="<?= (int)$p['id'] ?>">
                                            <?= htmlspecialchars($p['name']) ?>
                                        </option>
                                    <?php endif; ?>
                                <?php endforeach; ?>
                            </select>
                        </td>
                    </tr>
                </table>
            <?php endif; ?>
        </fieldset>

        <br>

        <!-- ESTÚDIOS -->
        <fieldset>
            <legend>Estúdios (Developer / Publisher)</legend>

            <?php if (empty($all_studios)): ?>
                <p>Não há estúdios ainda. Podes criar em baixo.</p>
            <?php else: ?>
                <h4>Developers</h4>
                <table>
                    <tr>
                        <td>
                            <strong>Disponíveis</strong><br>
                            <select id="studios_dev_available" multiple size="6">
                                <?php foreach ($all_studios as $s): ?>
                                    <?php if (!in_array((int)$s['id'], $current_devs, true)): ?>
                                        <option value="<?= (int)$s['id'] ?>">
                                            <?= htmlspecialchars($s['name']) ?>
                                        </option>
                                    <?php endif; ?>
                                <?php endforeach; ?>
                            </select>
                        </td>
                        <td style="padding: 0 10px; vertical-align: middle;">
                            <button type="button" onclick="moveSelected('studios_dev_available', 'studios_dev_selected')">
                                &gt;&gt;
                            </button>
                            <br><br>
                            <button type="button" onclick="moveSelected('studios_dev_selected', 'studios_dev_available')">
                                &lt;&lt;
                            </button>
                        </td>
                        <td>
                            <strong>Selecionados</strong><br>
                            <select name="studios_developer[]" id="studios_dev_selected" multiple size="6">
                                <?php foreach ($all_studios as $s): ?>
                                    <?php if (in_array((int)$s['id'], $current_devs, true)): ?>
                                        <option value="<?= (int)$s['id'] ?>">
                                            <?= htmlspecialchars($s['name']) ?>
                                        </option>
                                    <?php endif; ?>
                                <?php endforeach; ?>
                            </select>
                        </td>
                    </tr>
                </table>

                <h4>Publishers</h4>
                <table>
                    <tr>
                        <td>
                            <strong>Disponíveis</strong><br>
                            <select id="studios_pub_available" multiple size="6">
                                <?php foreach ($all_studios as $s): ?>
                                    <?php if (!in_array((int)$s['id'], $current_pubs, true)): ?>
                                        <option value="<?= (int)$s['id'] ?>">
                                            <?= htmlspecialchars($s['name']) ?>
                                        </option>
                                    <?php endif; ?>
                                <?php endforeach; ?>
                            </select>
                        </td>
                        <td style="padding: 0 10px; vertical-align: middle;">
                            <button type="button" onclick="moveSelected('studios_pub_available', 'studios_pub_selected')">
                                &gt;&gt;
                            </button>
                            <br><br>
                            <button type="button" onclick="moveSelected('studios_pub_selected', 'studios_pub_available')">
                                &lt;&lt;
                            </button>
                        </td>
                        <td>
                            <strong>Selecionados</strong><br>
                            <select name="studios_publisher[]" id="studios_pub_selected" multiple size="6">
                                <?php foreach ($all_studios as $s): ?>
                                    <?php if (in_array((int)$s['id'], $current_pubs, true)): ?>
                                        <option value="<?= (int)$s['id'] ?>">
                                            <?= htmlspecialchars($s['name']) ?>
                                        </option>
                                    <?php endif; ?>
                                <?php endforeach; ?>
                            </select>
                        </td>
                    </tr>
                </table>
            <?php endif; ?>

            <h4>Novo estúdio</h4>
            <label>
                Nome:<br>
                <input type="text" name="new_dev_name">
            </label>
            <br>
            <label>
                País:<br>
                <input type="text" name="new_dev_country" maxlength="100">
            </label>
            <button type="submit" name="action" value="add_dev">Criar estúdio Dev</button>
        </fieldset>

        <br>

        <button type="submit" name="action" value="save_all">Guardar jogo e ligações</button>
    </form>
</body>
</html>
