type Props = {
  sql: string;
};

export function SqlPanel({ sql }: Props) {
  return (
    <section className="sqlPanel">
      <p className="eyebrow">Generated SQL</p>
      <pre>{sql}</pre>
    </section>
  );
}
