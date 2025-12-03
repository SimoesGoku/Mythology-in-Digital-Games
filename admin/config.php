<?php
// config.php

// Caminho RELATIVO a partir da pasta admin
$dbPath = __DIR__ . '/../data/sqlite/mythology_in_digital_games.db';

try {
    $db = new PDO('sqlite:' . $dbPath);
    $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
    die('Erro na ligação à base de dados: ' . $e->getMessage());
}
