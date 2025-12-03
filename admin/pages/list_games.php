<?php
require_once __DIR__ . '/../config.php';

$games = $db->query('SELECT id, title, release_date FROM games ORDER BY title')
            ->fetchAll(PDO::FETCH_ASSOC);
?>
<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <title>Lista de jogos</title>
</head>
<body>
    <h1>Lista de jogos</h1>
    <p><a href="../index.php">← Voltar</a></p>
    <p><a href="add_game.php">+ Adicionar novo jogo</a></p>

    <?php if (empty($games)): ?>
        <p>Não há jogos na base de dados.</p>
    <?php else: ?>
        <table border="1" cellpadding="5" cellspacing="0">
            <tr>
                <th>ID</th>
                <th>Título</th>
                <th>Data</th>
                <th>Ações</th>
            </tr>
            <?php foreach ($games as $g): ?>
                <tr>
                    <td><?= (int)$g['id'] ?></td>
                    <td><?= htmlspecialchars($g['title']) ?></td>
                    <td><?= htmlspecialchars($g['release_date'] ?? '') ?></td>
                    <td>
                        <a href="edit_game.php?id=<?= (int)$g['id'] ?>">Editar ligações</a>
                    </td>
                </tr>
            <?php endforeach; ?>
        </table>
    <?php endif; ?>
</body>
</html>
