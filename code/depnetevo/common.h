/*
 * common.h
 *
 *  Created on: 28. juuli 2016
 *      Author: Riivo
 */

#ifndef COMMON_H_
#define COMMON_H_

#include <string>
#include <sstream>
#include <vector>
#include <ctime>
#include <iostream>
#include <functional>

inline void log(std::string str) {
    time_t t = time(0); // get time now
    struct tm * now = localtime(&t);
    std::cout << (now->tm_year + 1900) << '-' << (now->tm_mon + 1) << '-' << now->tm_mday;
    std::cout << " " << now->tm_hour << ":" << now->tm_min << ":" << now->tm_sec << ": ";
    std::cout << str << std::endl;
    std::cout.flush();

}

struct pairhash {
public:
    template<typename T, typename U>
    std::size_t operator()(const std::pair<T, U> &x) const {
        return std::hash<T>()(x.first) ^ std::hash<U>()(x.second);
    }
};

void split(const std::string &s, char delim, std::vector<string> &elems) {
    std::stringstream ss(s);
    std::string item;
    while (getline(ss, item, delim)) {
        elems.push_back(item);
    }
}

vector<std::string> split(const std::string &s, char delim) {
    vector<std::string> elems;
    split(s, delim, elems);
    return elems;
}

#endif /* COMMON_H_ */
