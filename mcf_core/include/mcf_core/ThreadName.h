/**
 * A thin wrapper around thread naming interfaces by both NVIDIA (via nvToolsExt) and pthread.
 *
 * Copyright (c) 2024 Accenture
 *
 */

#include <string>

namespace mcf
{
/**
 * @brief Set the current thread name
 *
 * For tracing/debugging purposes, it is often useful to correlate a thread id with a human-readable
 * name. In almost all cases, pthread_setname_np is completely sufficient, however, in the trace
 * generated by nvprof, this naming is not honored. Thus, this method provides a mechanism to set a
 * thread name on both interfaces.
 *
 * @param name The thread name. Only the first 15 characters will be considered.
 */
void setThreadName(const std::string& name);

} // namespace mcf
