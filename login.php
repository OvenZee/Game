<?php
// Database connection
$servername = "dbs.spskladno.cz";
$username = "student22"; // your db username
$password = "spsnet"; // your db password
$dbname = "vyuka22"; // your database name

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Get the submitted username and password
$username = $_POST['username'];
$password = $_POST['password'];

// Query to check if the username and password exist
$sql = "SELECT * FROM 1users WHERE username = '$username' AND password = '$password'";
$result = $conn->query($sql);

if ($result->num_rows > 0) {
    // Login successful, redirect to leaderboard
    session_start();
    $_SESSION['username'] = $username;
    header("Location: leaderboard.php");
} else {
    // Login failed
    echo "Invalid username or password.";
}

$conn->close();
?>