<?php
// File: upload.php
header('Content-Type: application/json');

// 1) Validate secret header
$secret = $_SERVER['HTTP_X_SECRET_KEY'] ?? '';
if ($secret !== 'MyUltraSecretKeyValue123!') {
    http_response_code(401);
    echo json_encode(['error' => 'Unauthorized']);
    exit;
}

// 2) Parse JSON body
$body = json_decode(file_get_contents('php://input'), true);
if (json_last_error() || empty($body['deviceId']) || empty($body['metric'])) {
    http_response_code(400);
    echo json_encode(['error' => 'Bad Request']);
    exit;
}

// 3) Insert into PostgreSQL and NOTIFY
try {
    $pdo = new PDO(
        'pgsql:host=db;port=5432;dbname=sensordb',
        'ssc',
        'ChangeMeToAStrongPass!'
    );
    $stmt = $pdo->prepare(
        'INSERT INTO telemetry (device_id, client_id, metric, value, ts)
         VALUES (:did, :cid, :metric, :value, NOW())'
    );
    $stmt->execute([
        ':did'    => $body['deviceId'],
        ':cid'    => $body['clientId'] ?? '',
        ':metric' => $body['metric'],
        ':value'  => $body['value']    ?? ''
    ]);

    // ─────────────────────────────────────────────────────────────────
    // Emit a PostgreSQL NOTIFY so our WebSocket service can push it live
    // ─────────────────────────────────────────────────────────────────
    $payload = json_encode([
        'id'        => $pdo->lastInsertId(),
        'deviceId'  => $body['deviceId'],
        'clientId'  => $body['clientId'] ?? '',
        'metric'    => $body['metric'],
        'value'     => $body['value']    ?? '',
        'ts'        => (new DateTime())->format(DateTime::ATOM),
    ]);
    // Quote the payload to escape any embedded quotes
    $quoted = $pdo->quote($payload);
    $pdo->exec("NOTIFY telemetry_channel, $quoted");

    // 4) Return success
    echo json_encode(['status' => 'OK']);
} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode(['error' => 'Database Error']);
}
