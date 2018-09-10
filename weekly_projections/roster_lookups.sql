select
team,
name,
position,
range,
points,
count
from rosters
left join (
    select
    name,
    position,
    round(avg(points), 1) as points,
    (round(min(points), 1) || '-' || round(max(points), 1)) as range,
    count(*) as count
    from projections
    where week = 1
    group by 1, 2
    having count(*) > 1
    order by 3 desc
) averages using (name, position)
where team in ('TacoCorp', 'phantasy')
order by points desc
