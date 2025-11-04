package routes

import (
	"product-service/controllers"
	"product-service/middleware"

	"github.com/gin-gonic/gin"
)

func SetupRoutes(r *gin.Engine) {
	items := r.Group("/items")
	items.Use(middleware.AuthMiddleware())
	{
		items.GET("", controllers.GetItems)
		items.GET("/:id", controllers.GetItem)
		items.POST("", controllers.CreateItem)
		items.PUT("/:id", controllers.UpdateItem)
		items.DELETE("/:id", controllers.DeleteItem)
	}

	categories := r.Group("/categories")
	{
		categories.GET("", controllers.GetCategories)
		categories.POST("", controllers.CreateCategory)
	}

	bids := r.Group("/bids")
	bids.Use(middleware.AuthMiddleware())
	{
		bids.GET("/:item_id", controllers.GetBids)
		bids.POST("", controllers.CreateBid)
	}
}
