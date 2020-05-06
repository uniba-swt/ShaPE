entry(This)  :-  node(This), next(This, Next), prev(This, This), p(Next, This), true.
p(This, P1)  :-  node(This), next(This, This), prev(This, P1), true, true.
p(This, P1)  :-  node(This), next(This, Next), prev(This, P1), p(Next, This), true.