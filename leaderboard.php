<?php
session_start();
if (!isset($_SESSION['username'])) {
    header("Location: login.html");
    exit();
}

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

// Query to get the top 10 scores and usernames
$sql = "SELECT 1users.username, 1score.score FROM 1score
        JOIN 1users ON 1score.player_id = 1users.id
        ORDER BY 1score.score DESC LIMIT 10";

$result = $conn->query($sql);

echo "<h2>Leaderboard</h2>";
echo "<table border='1'>
        <tr>
            <th>Rank</th>
            <th>Username</th>
            <th>Score</th>
        </tr>";

if ($result->num_rows > 0) {
    $rank = 1;
    while ($row = $result->fetch_assoc()) {
        echo "<tr>
                <td>$rank</td>
                <td>" . $row['username'] . "</td>
                <td>" . $row['score'] . "</td>
              </tr>";
        $rank++;
    }
    echo "</table>";
} else {
    echo "No scores available.";
}

$conn->close();
?>