package main

import (
	"database/sql"
	"flag"
	"fmt"
	"log"
	"os"
	"time"

	"golang.org/x/crypto/bcrypt"
	_ "modernc.org/sqlite"
)

func must(err error) {
	if err != nil {
		log.Fatal(err)
	}
}

func createGatewayDB(path string) {
	os.MkdirAll("gateway", 0755)
	db, err := sql.Open("sqlite", path)
	must(err)
	defer db.Close()

	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT,
    address TEXT,
    phone TEXT,
    profile_picture TEXT,
    date_joined DATETIME DEFAULT CURRENT_TIMESTAMP,
    rating REAL DEFAULT 0
);`)
	must(err)

	hash, err := bcrypt.GenerateFromPassword([]byte("password123"), bcrypt.DefaultCost)
	must(err)

	_, err = db.Exec(`INSERT OR IGNORE INTO users (username, email, password_hash, full_name, address, phone, profile_picture, date_joined, rating)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);`, "demo", "demo@example.com", string(hash), "Demo User", "123 Demo St", "555-0100", "", time.Now(), 4.5)
	must(err)

	fmt.Println("Created/updated gateway DB:", path)
}

func createProductDB(path string) {
	os.MkdirAll("product-service", 0755)
	db, err := sql.Open("sqlite", path)
	must(err)
	defer db.Close()

	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS items (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    seller_id INTEGER,
    title TEXT,
    description TEXT,
    price REAL,
    quantity INTEGER,
    is_auction INTEGER,
    start_price REAL,
    start_date DATETIME,
    end_date DATETIME,
    status TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);`)
	must(err)

	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT,
    parent_category_id INTEGER
);`)
	must(err)

	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS item_images (
    image_id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER,
    image_url TEXT
);`)
	must(err)

	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS bids (
    bid_id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER,
    bidder_id INTEGER,
    bid_amount REAL,
    bid_time DATETIME DEFAULT CURRENT_TIMESTAMP
);`)
	must(err)

	_, err = db.Exec(`INSERT OR IGNORE INTO categories (category_id, category_name, parent_category_id) VALUES (1, 'Electronics', NULL);`)
	must(err)
	_, err = db.Exec(`INSERT OR IGNORE INTO categories (category_id, category_name, parent_category_id) VALUES (2, 'Laptops', 1);`)
	must(err)

	start := time.Now().Add(-24 * time.Hour)
	end := time.Now().Add(7 * 24 * time.Hour)
	_, err = db.Exec(`INSERT OR IGNORE INTO items (item_id, seller_id, title, description, price, quantity, is_auction, start_price, start_date, end_date, status, created_at)
    VALUES (1, 1, 'Demo Laptop', 'A lightly used demo laptop', 499.99, 1, 0, 0, ?, ?, 'active', ?);`, start, end, time.Now())
	must(err)

	_, err = db.Exec(`INSERT OR IGNORE INTO item_images (image_id, item_id, image_url) VALUES (1,1,'http://example.com/laptop.jpg');`)
	must(err)

	_, err = db.Exec(`INSERT OR IGNORE INTO bids (bid_id, item_id, bidder_id, bid_amount, bid_time) VALUES (1, 1, 2, 520.00, ?);`, time.Now())
	must(err)

	fmt.Println("Created/updated product DB:", path)
}

func verifyGateway(path string) {
	db, err := sql.Open("sqlite", path)
	must(err)
	defer db.Close()

	fmt.Println("\nGateway DB:", path)
	row := db.QueryRow("SELECT user_id, username, email, full_name, date_joined FROM users LIMIT 1;")
	var id int
	var username, email, fullName, dateJoined string
	if err := row.Scan(&id, &username, &email, &fullName, &dateJoined); err != nil {
		fmt.Println("  no rows or error:", err)
		return
	}
	fmt.Printf("  sample user: id=%d username=%s email=%s full_name=%s date_joined=%s\n", id, username, email, fullName, dateJoined)
}

func verifyProduct(path string) {
	db, err := sql.Open("sqlite", path)
	must(err)
	defer db.Close()

	fmt.Println("\nProduct DB:", path)
	row := db.QueryRow("SELECT item_id, seller_id, title, price, status FROM items LIMIT 1;")
	var itemID, sellerID int
	var title, status string
	var price float64
	if err := row.Scan(&itemID, &sellerID, &title, &price, &status); err != nil {
		fmt.Println("  no rows or error:", err)
		return
	}
	fmt.Printf("  sample item: id=%d seller_id=%d title=%s price=%.2f status=%s\n", itemID, sellerID, title, price, status)

	var bidsCount int
	err = db.QueryRow("SELECT COUNT(*) FROM bids WHERE item_id = ?", itemID).Scan(&bidsCount)
	if err == nil {
		fmt.Printf("  bids for item %d: %d\n", itemID, bidsCount)
	}
}

func printUsage() {
	fmt.Println("Usage: go run scripts/tool.go <command>")
	fmt.Println("Commands:")
	fmt.Println("  seed     Create or seed the SQLite databases (gateway/product-service)")
	fmt.Println("  verify   Print a sample row from each DB to verify seed")
}

func main() {
	flag.Parse()
	if flag.NArg() < 1 {
		printUsage()
		os.Exit(1)
	}

	cmd := flag.Arg(0)
	gatewayDB := "gateway/gateway.db"
	productDB := "product-service/product.db"

	switch cmd {
	case "seed":
		createGatewayDB(gatewayDB)
		createProductDB(productDB)
		fmt.Println("Done. Files created:")
		fmt.Println(" -", gatewayDB)
		fmt.Println(" -", productDB)
	case "verify":
		verifyGateway(gatewayDB)
		verifyProduct(productDB)
	default:
		printUsage()
		os.Exit(1)
	}
}
