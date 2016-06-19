def Summarize(markdown, limit=1000):
  """Returns a string with the beginning of a markdown article.

  Args:
    markdown: string, containing the original article in markdown format.
    limit: integer, how many characters of the original article to produce
      in the summary before starting to look for a good place to stop it.

  Returns:
    string, a markdown summary of at least limit length, unless the article
    is shorter.
  """
  import itertools

  summary = []
  count = 0

  # Skip titles, we don't want titles in summaries.
  def ShouldLineBeSkipped(line):
    if line and line[0] == '#':
      return True
    return False

  # Create an iterator to go over all lines.
  lines = itertools.ifilter(SholdLineBeSkipped, markdown.splitlines())

  # Save all lines until we reach our limit.
  for line in lines:
    summary.append(line)

    count += len(line)
    if count >= limit:
      break

  # Save lines until we find a good place to break the article.
  for line in lines:
    # Keep going until what could be the end of a paragraph.
    if not line.strip() and summary[-1] and summary[-1][-1] == ".":
      break
    summary.append(line)

  # Add an empty line, and bolded '...' at the end of the summary.
  summary.append("")
  summary.append("**[ ... ]**")

  # Finally, return the summary.
  return "\n".join(summary)