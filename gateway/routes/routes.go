package routes

import (
	"gateway/controllers"
	"gateway/middleware"

	"github.com/gin-gonic/gin"
)

func SetupRoutes(r *gin.Engine) {
	auth := r.Group("/auth")
	{
		auth.POST("/register", controllers.Register)
		auth.POST("/login", controllers.Login)
		auth.GET("/verify", controllers.Verify)
	}

	proxy := r.Group("/proxy")
	proxy.Use(middleware.AuthMiddleware())
	{
		proxy.GET("/items", controllers.ProxyItems)
		proxy.POST("/items", controllers.ProxyItems)
		proxy.GET("/items/:id", controllers.ProxyItem)
		proxy.PUT("/items/:id", controllers.ProxyItem)
		proxy.DELETE("/items/:id", controllers.ProxyItem)
		proxy.GET("/categories", controllers.ProxyCategories)
		proxy.POST("/categories", controllers.ProxyCategories)
		proxy.GET("/bids/:item_id", controllers.ProxyBids)
		proxy.POST("/bids", controllers.ProxyBids)
	}
}
