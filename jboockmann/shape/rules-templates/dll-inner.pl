entry(This)  :-  node(This), next(This, Next), prev(This, Prev), p(Prev, This), p(Next, This), true.
p(This, P1)  :-  node(This), next(This, P1), prev(This, null), true, true.
p(This, P1)  :-  node(This), next(This, null), prev(This, P1), true, true.
p(This, P1)  :-  node(This), next(This, Next), prev(This, P1), p(Next, This), true.
p(This, P1)  :-  node(This), next(This, P1), prev(This, Prev), p(Prev, This), true.