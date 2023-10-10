package main

import (
	"os"
	"strconv"
	"strings"

	"encoding/json"

	"github.com/gofiber/contrib/websocket"
	fiber "github.com/gofiber/fiber/v2"
)

func read_data() Data {
	file, err := os.Open("./data.json")
	if err != nil {
		panic(err)
	}
	defer file.Close()
	var data Data
	err = json.NewDecoder(file).Decode(&data)
	if err != nil {
		panic(err)
	}
	return data
}

func main() {
	app := fiber.New()

	if _, err := os.Stat("./data.json"); os.IsNotExist(err) {
		// create file + write data
		os.Create("./data.json")
		data := Data{
			Lidar: [810]float64{},
		}
		file, err := os.OpenFile("./data.json", os.O_RDWR, 0644)
		if err != nil {
			panic(err)
		}
		defer file.Close()
		// write to json file
		err = json.NewEncoder(file).Encode(data)
		if err != nil {
			panic(err)
		}

	}

	// /lidar with websocket
	app.Get("/lidar", websocket.New(func(c *websocket.Conn) {
		for {
			mt, msg, err := c.ReadMessage()
			if err != nil {
				println("read:", err.Error())
				return
			}
			// if message contain get, send data
			if strings.Split(string(msg), ":")[0] == "get" {
				// read data from file
				data := read_data()
				// send data
				lidar_byte := []byte{}
				for _, v := range data.Lidar {
					lidar_byte = append(lidar_byte, []byte(strconv.FormatFloat(v, 'f', 4, 64))...)
					lidar_byte = append(lidar_byte, []byte(",")...)
				}
				err = c.WriteMessage(mt, append([]byte("current:"), lidar_byte...))
				if err != nil {
					println("write:", err.Error())
					return
				}
				continue
			}
			if strings.Split(string(msg), ":")[0] == "set" {
				// read data from ws message
				lidar := strings.Split(string(msg), ":")[1]
				// convert to []float64
				lidar_float := []float64{}
				for _, v := range strings.Split(lidar, ",") {
					f, err := strconv.ParseFloat(v, 64)
					if err != nil {
						panic(err)
					}
					lidar_float = append(lidar_float, f)
				}
				// send data to file
				file, err := os.OpenFile("./data.json", os.O_RDWR, 0644)
				if err != nil {
					panic(err)
				}
				defer file.Close()

				data := Data{
					Lidar: [810]float64(lidar_float),
				}
				// write to json file
				err = json.NewEncoder(file).Encode(data)
				if err != nil {
					panic(err)
				}
				// emit message to all client
				err = c.WriteMessage(mt, []byte("new:"+strings.Split(string(msg), ":")[1]))
				if err != nil {
					println("write:", err.Error())
					return
				}
				continue

			}

			println("recv: ", string(msg))

			err = c.WriteMessage(mt, msg)
			if err != nil {
				println("write:", err.Error())
				return
			}
		}
	}))
	app.Listen(":3000")
}

type Data struct {
	Lidar [810]float64
}
