package models

import (
	"time"
)

type Item struct {
	ItemID      uint      `json:"item_id" gorm:"primaryKey;autoIncrement"`
	SellerID    uint      `json:"seller_id"`
	Title       string    `json:"title"`
	Description string    `json:"description"`
	Price       float64   `json:"price"`
	Quantity    int       `json:"quantity"`
	IsAuction   bool      `json:"is_auction"`
	StartPrice  float64   `json:"start_price"`
	StartDate   time.Time `json:"start_date"`
	EndDate     time.Time `json:"end_date"`
	Status      string    `json:"status"`
	CreatedAt   time.Time `json:"created_at" gorm:"autoCreateTime"`
}

type Category struct {
	CategoryID       uint   `json:"category_id" gorm:"primaryKey;autoIncrement"`
	CategoryName     string `json:"category_name"`
	ParentCategoryID *uint  `json:"parent_category_id"`
}

type ItemImage struct {
	ImageID  uint   `json:"image_id" gorm:"primaryKey;autoIncrement"`
	ItemID   uint   `json:"item_id"`
	ImageURL string `json:"image_url"`
}

type Bid struct {
	BidID     uint      `json:"bid_id" gorm:"primaryKey;autoIncrement"`
	ItemID    uint      `json:"item_id"`
	BidderID  uint      `json:"bidder_id"`
	BidAmount float64   `json:"bid_amount"`
	BidTime   time.Time `json:"bid_time" gorm:"autoCreateTime"`
}
