package main

import "fmt"

func main() {
    var N, H, G, M int

    fmt.Scanln(&N)
    fmt.Scanln(&H)
    fmt.Scanln(&G)
    fmt.Scanln(&M)

    totalFatias := (H * 12) + (G * 8) + (M * 6)

    fatiasSobrantes := 0
    if totalFatias > N {
        fatiasSobrantes = totalFatias - N
    }

    fmt.Println(fatiasSobrantes)
}

