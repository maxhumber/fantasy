select
team,
name,
position,
points,
range
from (
	select
	name,
	position,
	round(avg(points), 1) as points,
	(round(min(points), 1) || '-' || round(max(points), 1)) as range
	from projections
	where
	season = 2018 and
	week = 2 and
	strftime('%Y-%m-%d', fetched_at) = (
		select
		max(strftime('%Y-%m-%d', fetched_at))
		from projections
	)
	group by 1, 2
	having count(*) > 1
) projections
left join (
	select
	*
	from rosters
	where
	strftime('%Y-%m-%d', fetched_at) = (
		select
		max(strftime('%Y-%m-%d', fetched_at))
		from projections
	)
) rosters using (name, position)
where team in ('phantasy', 'Forgetting Brandon Marshall')
order by points desc
