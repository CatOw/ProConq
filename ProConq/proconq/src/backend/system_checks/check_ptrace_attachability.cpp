#include <iostream>
#include <sys/ptrace.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

int main(int argc, char* argv[]) {
  if (argc != 2) {
    std::cerr << "Usage: " << argv[0] << " PID\n";
    return 1;
  }

  pid_t pid = std::stoi(argv[1]);

  if (ptrace(PTRACE_ATTACH, pid, nullptr, nullptr) == -1) {
    std::cerr << "Cannot attach to PID " << pid << "\n";
    return 1;
  }

  int status;
  waitpid(pid, &status, 0);

  if (WIFSTOPPED(status)) {
    std::cout << "PID " << pid << " is attachable by ptrace\n";
  } else {
    std::cerr << "Cannot attach to PID " << pid << "\n";
    return 1;
  }

  ptrace(PTRACE_DETACH, pid, nullptr, nullptr);

  return 0;
}
