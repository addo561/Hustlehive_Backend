package controllers

import (
	"net/http"
	"product-service/database"
	"product-service/models"

	"github.com/gin-gonic/gin"
)

func GetBids(c *gin.Context) {
	itemID := c.Param("item_id")
	var bids []models.Bid
	database.DB.Where("item_id = ?", itemID).Find(&bids)
	c.JSON(http.StatusOK, bids)
}

func CreateBid(c *gin.Context) {
	var bid models.Bid
	if err := c.ShouldBindJSON(&bid); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	bidderID, exists := c.Get("user_id")
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Unauthorized"})
		return
	}

	bid.BidderID = bidderID.(uint)

	if err := database.DB.Create(&bid).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create bid"})
		return
	}

	c.JSON(http.StatusCreated, bid)
}
