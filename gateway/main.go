package main

import (
	"gateway/database"
	"gateway/routes"
	"log"
	"os"

	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"
)

func main() {
	err := godotenv.Load()
	if err != nil {
		log.Fatal("Error loading .env file")
	}

	database.InitDB()

	r := gin.Default()
	routes.SetupRoutes(r)

	port := os.Getenv("GATEWAY_PORT")
	if port == "" {
		port = "8080"
	}

	r.Run(":" + port)
}
