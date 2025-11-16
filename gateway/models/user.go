package models

import (
	"time"
)

type User struct {
	UserID         uint      `json:"user_id" gorm:"primaryKey;autoIncrement"`
	Username       string    `json:"username" gorm:"unique;not null"`
	Email          string    `json:"email" gorm:"unique;not null"`
	PasswordHash   string    `json:"-" gorm:"not null"`
	FullName       string    `json:"full_name"`
	Address        string    `json:"address"`
	Phone          string    `json:"phone"`
	ProfilePicture string    `json:"profile_picture"`
	DateJoined     time.Time `json:"date_joined" gorm:"autoCreateTime"`
	Rating         float64   `json:"rating" gorm:"default:0"`
}
