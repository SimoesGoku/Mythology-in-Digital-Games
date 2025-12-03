<?php
require_once __DIR__ . '/../config.php';

$mensagem = '';
$novoId = null;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $title = trim($_POST['title'] ?? '');
    $release_date = trim($_POST['release_date'] ?? '');

    if ($title === '') {
        $mensagem = 'Título é obrigatório.';
    } else {
        $stmt = $db->prepare('INSERT INTO games (title, release_date) VALUES (:title, :release_date)');
        $stmt->execute([
            ':title' => $title,
            ':release_date' => $release_date !== '' ? $release_date : null,
        ]);
        $novoId = (int)$db->lastInsertId();
        $mensagem = 'Jogo adicionado com sucesso.';
    }
}
?>
<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <title>Adicionar jogo</title>
</head>
<body>
    <h1>Adicionar jogo</h1>
    <p><a href="../index.php">← Voltar</a></p>

    <?php if ($mensagem): ?>
        <p><strong><?= htmlspecialchars($mensagem) ?></strong></p>
    <?php endif; ?>

    <?php if ($novoId): ?>
        <p>
            <a href="edit_game.php?id=<?= $novoId ?>">Editar ligações deste jogo agora</a>
        </p>
    <?php endif; ?>

    <form method="post">
        <label>
            Título:<br>
            <input type="text" name="title" required>
        </label>
        <br><br>
        <label>
            Data de lançamento (YYYY ou YYYY-MM-DD):<br>
            <input type="text" name="release_date">
        </label>
        <br><br>
        <button type="submit">Guardar</button>
    </form>
</body>
</html>
