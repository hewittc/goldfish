goldfish
--------

A live Linux process memory viewer (eventually).

note
----

The Yama Linux Security Module disables ptracing to a non-child 
process as a non-root user by default. Enable the classic ptrace 
permissions by:

    echo 0 | sudo tee /proc/sys/kernel/yama/ptrace_scope

Possible ptrace_scope sysctl values:
    
    0 - classic ptrace permissions: a process can PTRACE_ATTACH to any other
        process running under the same uid, as long as it is dumpable (i.e.
        did not transition uids, start privileged, or have called
        prctl(PR_SET_DUMPABLE...) already). Similarly, PTRACE_TRACEME is
        unchanged.

    1 - restricted ptrace: a process must have a predefined relationship
        with the inferior it wants to call PTRACE_ATTACH on. By default,
        this relationship is that of only its descendants when the above
        classic criteria is also met. To change the relationship, an
        inferior can call prctl(PR_SET_PTRACER, debugger, ...) to declare
        an allowed debugger PID to call PTRACE_ATTACH on the inferior.
        Using PTRACE_TRACEME is unchanged.

    2 - admin-only attach: only processes with CAP_SYS_PTRACE may use ptrace
        with PTRACE_ATTACH, or through children calling PTRACE_TRACEME.

    3 - no attach: no processes may use ptrace with PTRACE_ATTACH nor via
        PTRACE_TRACEME. Once set, this sysctl value cannot be changed.

Source: https://www.kernel.org/doc/Documentation/security/Yama.txt

