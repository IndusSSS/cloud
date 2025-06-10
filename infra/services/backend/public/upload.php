<?php
// Very simple file receiver — replace with your auth logic
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo "Method Not Allowed";
    exit;
}

$target = __DIR__ . '/uploads';
if (!is_dir($target)) mkdir($target, 0775, true);

$fname = $target . '/' . basename($_FILES['file']['name'] ?? 'upload.bin');
if (move_uploaded_file($_FILES['file']['tmp_name'], $fname)) {
    echo "✅ Uploaded to $fname";
} else {
    http_response_code(400);
    echo "❌ Failed";
}
