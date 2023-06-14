#include <iostream>
#include <fstream>
#include <unistd.h>
#include <sys/syscall.h>
#include <fcntl.h>
#include <cstdlib>
#include <cstring>

using namespace std;

int main() {
    int pid = getpid();
    printf("PID: %d\n", pid);

    printf("Press enter to open bad.txt\n");
    getchar();
    int fd = syscall(SYS_open, "bad.txt", O_RDONLY);
    cout << "open returned " << fd << endl;

    if (fd == -1) {
        cerr << "Failed to open file\n";
        return 1;
    }

    char buffer[1024];
    ssize_t num_read;

    while ((num_read = read(fd, buffer, sizeof(buffer))) > 0) {
        if (write(STDOUT_FILENO, buffer, num_read) == -1) {
            cerr << "Failed to write to stdout\n";
            syscall(SYS_close, fd);
            return 1;
        }
    }

    if (num_read == -1) {
        cerr << "Failed to read from file\n";
        syscall(SYS_close, fd);
        return 1;
    }

    syscall(SYS_close, fd);
    return 0;
}