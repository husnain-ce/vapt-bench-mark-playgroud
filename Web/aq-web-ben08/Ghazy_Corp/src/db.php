<?php

error_reporting(0);
$servername = "db";
$username = "ctf";
$password = "ctf123";
$dbname = "ghazycorp";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
	die("Connection failed: " . $conn->connect_error);
}

?>